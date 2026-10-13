"""Offline regression checks for real generation, source failures, and CI churn."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

from models import FeedConfig, load_feed_registry
from run_all_feeds import run_feed
from utils import _preserve_unchanged_feed

FIXTURES = Path(__file__).parent / "fixtures"


class CIReliabilityTests(unittest.TestCase):
    def test_real_offline_generator_is_stable_but_must_write_each_run(self):
        config = FeedConfig(
            script=str((FIXTURES / "offline_generator.py").resolve()),
            type="requests",
            blog_url="https://example.invalid/blog",
        )
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            summary = folder / "summary.md"
            with (
                patch("run_all_feeds.get_feeds_dir", return_value=folder),
                patch.dict(
                    os.environ,
                    {
                        "RSS_TEST_OUTPUT": tmp,
                        "RSS_TEST_BUILD_DAY": "1",
                        "GITHUB_STEP_SUMMARY": str(summary),
                        "UV_OFFLINE": "true",
                        "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "feed_generators"),
                    },
                ),
            ):
                self.assertTrue(run_feed("fixture", config))
                path = folder / "feed_fixture.xml"
                original = path.read_bytes()
                os.utime(path, ns=(1, 1))
                os.environ["RSS_TEST_BUILD_DAY"] = "2"
                self.assertTrue(run_feed("fixture", config))
                self.assertEqual(path.read_bytes(), original)
                self.assertNotEqual(path.stat().st_mtime_ns, 1)

                os.environ["RSS_TEST_TITLE"] = "Corrected article"
                self.assertTrue(run_feed("fixture", config))
                updated = path.read_bytes()
                self.assertNotEqual(updated, original)
                self.assertEqual(ET.fromstring(updated).findtext("channel/item/guid"), "stable-fixture-guid")

                os.environ["RSS_TEST_SKIP_WRITE"] = "1"
                self.assertFalse(run_feed("fixture", config))
                self.assertEqual(path.read_bytes(), updated)
                self.assertIn("exited without writing fresh output", summary.read_text())
                self.assertIn("| 4 | ❌ | fixture |", summary.read_text())

    def test_comparison_retains_real_metadata_changes_and_repairs_bad_history(self):
        original = b"<rss><channel><title>Old</title><lastBuildDate>A</lastBuildDate></channel></rss>"
        changed = original.replace(b"Old", b"New").replace(b">A<", b">B<")
        self.assertEqual(_preserve_unchanged_feed(changed, original), changed)
        self.assertEqual(_preserve_unchanged_feed(changed, b"not XML"), changed)

    def test_registry_has_unique_output_paths(self):
        registry = load_feed_registry()
        paths = [config.output_name or name for name, config in registry.items()]
        self.assertEqual(len(paths), len(set(paths)))
