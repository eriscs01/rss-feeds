import argparse
import html
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from models import FeedConfig, FeedType, disable_feeds, load_feed_registry
from utils import get_feeds_dir
from validate_feeds import validate_feed

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Failure detail per feed from the current process, for --failures-file.
FAILURE_DETAILS: dict[str, str] = {}


def _report_result(feed_name: str, success: bool, detail: str) -> bool:
    """Append a per-feed outcome to GitHub's job summary and return its success.

    How:
    1. Leave local runs unchanged when no GitHub summary path is configured.
    2. Escape publisher/error text and append a numbered result row.
    3. Preserve the actual failure status; reporting never converts failure to success.
    """
    if not success:
        FAILURE_DETAILS[feed_name] = detail
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        path = Path(summary)
        existing = path.read_text() if path.exists() else ""
        cells = [html.escape(value).replace("|", "&#124;").replace("\n", " ") for value in (feed_name, detail)]
        number = max(1, sum(line.startswith("| ") for line in existing.splitlines()))
        with path.open("a") as handle:
            if not existing:
                handle.write("## Live feed refresh\n\n| # | Severity | Feed | Result |\n|---|---|---|---|\n")
            handle.write(f"| {number} | {'✅' if success else '❌'} | {cells[0]} | {cells[1]} |\n")
    return success


def run_feed(feed_name: str, config: FeedConfig, full: bool = False) -> bool:
    """Run a generator and require a refreshed, valid subscriber feed.

    How:
    1. Record the expected output file's modification time.
    2. Run the registered script and inspect its exit status.
    3. Reject missing, unchanged, empty, malformed, or duplicate-filled output.

    Args:
        feed_name: Registry name of the feed.
        config: Validated feed configuration.
        full: If True, pass --full flag to the generator.

    Returns:
        True if the generator succeeded, False otherwise.
    """
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.script)
    cmd = ["uv", "run", script_path]
    if full:
        cmd.append("--full")

    output = get_feeds_dir() / f"feed_{config.output_name or feed_name}.xml"
    previous_mtime = output.stat().st_mtime_ns if output.exists() else None
    logger.info(f"Running {feed_name}: {script_path}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        logger.error("🚨 %s exceeded the 10-minute generation timeout", feed_name)
        return _report_result(feed_name, False, "Generator exceeded the 10-minute timeout; refresh failed")
    if result.returncode == 0:
        if not output.exists() or output.stat().st_mtime_ns == previous_mtime:
            logger.error(
                "🚨 %s exited without refreshing %s. Generator output:\n%s\n%s",
                feed_name,
                output,
                result.stdout,
                result.stderr,
            )
            return _report_result(feed_name, False, "Generator exited without writing fresh output")
        validation = validate_feed(output)
        if validation["status"] in {"EMPTY", "ERROR"}:
            logger.error("🚨 %s produced an invalid feed: %s", feed_name, validation["message"])
            return _report_result(feed_name, False, f"Invalid generated XML: {validation['message']}")
        logger.info(f"Successfully ran: {feed_name}")
        deferred = [
            line.split("Scheduled entry deferred: ", 1)[1]
            for line in result.stderr.splitlines()
            if "Scheduled entry deferred: " in line
        ]
        for detail in deferred:
            logger.info("Scheduled entry deferred: %s", detail)
        detail = f"Refreshed and validated: {validation['message']}"
        if deferred:
            detail += f"; {len(deferred)} scheduled entries deferred: " + "; ".join(deferred)
        return _report_result(feed_name, True, detail)
    else:
        logger.error(f"Error running {feed_name}:\n{result.stderr}")
        errors = [line.strip() for line in result.stderr.splitlines() if "Error" in line or "Exception" in line]
        detail = errors[-1][:400] if errors else f"Generator exited with status {result.returncode}; see logs"
        return _report_result(feed_name, False, f"Refresh failed: {detail}")


def run_all_feeds(
    skip_selenium: bool = False,
    selenium_only: bool = False,
    feed: str | None = None,
    full: bool = False,
    disable_failed: bool = False,
    failures_file: str | None = None,
) -> int:
    """Run feed generators from the registry.

    Args:
        skip_selenium: Skip Selenium-based generators (for hourly requests workflow).
        selenium_only: Run only Selenium-based generators (for hourly Selenium workflow).
        feed: Run a single feed by name. Overrides skip_selenium/selenium_only.
        full: Pass --full flag to generators (full reset instead of incremental).
        disable_failed: Set `enabled: false` in feeds.yaml for each failed feed (multi-feed mode only).
        failures_file: Write failed feeds as JSON for the workflow to file issues (multi-feed mode only).

    Returns:
        Exit code (0 for success, 1 if any feed failed).
    """
    registry = load_feed_registry()

    # Single feed mode
    if feed:
        if feed not in registry:
            logger.error(f"Feed '{feed}' not found in registry. Available: {', '.join(sorted(registry))}")
            return 1
        config = registry[feed]
        if not config.enabled:
            logger.warning(f"Feed '{feed}' is disabled in feeds.yaml")
            return 1
        ok = run_feed(feed, config, full=full)
        return 0 if ok else 1

    # Multi-feed mode
    failed_scripts = []
    successful_scripts = []
    skipped_scripts = []

    for name, config in sorted(registry.items()):
        if not config.enabled:
            logger.info(f"Skipping disabled feed: {name}")
            skipped_scripts.append(name)
            continue

        is_selenium = config.type == FeedType.SELENIUM

        if skip_selenium and is_selenium:
            logger.info(f"Skipping Selenium generator: {name}")
            skipped_scripts.append(name)
            continue

        if selenium_only and not is_selenium:
            logger.info(f"Skipping non-Selenium generator: {name}")
            skipped_scripts.append(name)
            continue

        ok = run_feed(name, config, full=full)
        if ok:
            successful_scripts.append(name)
        else:
            failed_scripts.append(name)

    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info("Feed Generation Summary:")
    logger.info(f"  Successful: {len(successful_scripts)}")
    logger.info(f"  Failed: {len(failed_scripts)}")
    logger.info(f"  Skipped: {len(skipped_scripts)}")

    if successful_scripts:
        logger.info("\nSuccessful feeds:")
        for name in successful_scripts:
            logger.info(f"  ✓ {name}")

    if failures_file:
        failures = [
            {
                "name": name,
                "script": registry[name].script,
                "blog_url": registry[name].blog_url,
                "detail": FAILURE_DETAILS.get(name, "Refresh failed; see logs"),
            }
            for name in failed_scripts
        ]
        Path(failures_file).write_text(json.dumps(failures, indent=2))

    if failed_scripts:
        logger.error("\nFailed feeds:")
        for name in failed_scripts:
            logger.error(f"  ✗ {name}")
        if disable_failed:
            for name in disable_feeds(failed_scripts):
                logger.warning(f"Disabled failing feed in feeds.yaml: {name}")
        logger.error(f"\nERROR: {len(failed_scripts)} feed(s) failed to generate")
        return 1

    if skipped_scripts:
        logger.info("\nSkipped feeds:")
        for name in skipped_scripts:
            logger.info(f"  ○ {name}")

    logger.info(f"{'=' * 60}\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RSS feed generators")
    parser.add_argument(
        "--skip-selenium",
        action="store_true",
        help="Skip Selenium-based generators (for hourly requests workflow)",
    )
    parser.add_argument(
        "--selenium-only",
        action="store_true",
        help="Run only Selenium-based generators (for hourly Selenium workflow)",
    )
    parser.add_argument(
        "--feed",
        type=str,
        help="Run a single feed by name (e.g., --feed=ollama)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Pass --full to generators (full reset instead of incremental)",
    )
    parser.add_argument(
        "--disable-failed",
        action="store_true",
        help="Set enabled: false in feeds.yaml for each feed that fails (ignored with --feed)",
    )
    parser.add_argument(
        "--failures-file",
        type=str,
        help="Write failed feeds as JSON to this path (ignored with --feed)",
    )
    args = parser.parse_args()

    if args.skip_selenium and args.selenium_only:
        logger.error("Cannot use both --skip-selenium and --selenium-only")
        sys.exit(1)

    exit_code = run_all_feeds(
        skip_selenium=args.skip_selenium,
        selenium_only=args.selenium_only,
        feed=args.feed,
        full=args.full,
        disable_failed=args.disable_failed,
        failures_file=args.failures_file,
    )
    sys.exit(exit_code)
