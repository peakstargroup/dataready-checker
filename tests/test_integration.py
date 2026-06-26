import json
import tempfile
import unittest
from pathlib import Path

from peakstar_dataready import collect, report as report_mod
from peakstar_dataready.analyze import build_report
from tests import helpers as h


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.clean = h.make_clean(self.root)
        self.medium = h.make_medium(self.root)
        self.dirty = h.make_dirty(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _report(self, folder):
        files = collect.walk(folder)
        return build_report(files, str(folder))

    def test_score_ordering(self):
        clean = self._report(self.clean)
        medium = self._report(self.medium)
        dirty = self._report(self.dirty)
        self.assertGreater(clean.total_score, medium.total_score)
        self.assertGreater(medium.total_score, dirty.total_score)

    def test_lights(self):
        self.assertNotEqual(self._report(self.clean).light, "red")
        self.assertEqual(self._report(self.dirty).light, "red")

    def test_dirty_flags_scanned(self):
        codes = {f["code"] for f in self._report(self.dirty).findings}
        self.assertIn("SCANNED_PDF", codes)

    def test_dirty_has_higher_failure_rate(self):
        self.assertGreater(self._report(self.dirty).expected_failure_rate,
                           self._report(self.clean).expected_failure_rate)

    def test_walk_filters(self):
        only_md = collect.walk(self.clean, include=["*.md"])
        self.assertTrue(all(f.ext == ".md" for f in only_md))

    def test_html_and_json_outputs(self):
        report = self._report(self.dirty)
        out = self.root / "out"
        written = report_mod.write_reports(report, out, ["html", "json"], "zh")
        self.assertEqual(len(written), 2)
        html_txt = (out / "report.html").read_text(encoding="utf-8")
        json_txt = (out / "report.json").read_text(encoding="utf-8")
        # 品牌規則：報告本文不得含 em-dash
        self.assertNotIn("—", html_txt)
        self.assertNotIn("—", json_txt)
        # CTA 連到 Peakstar 官網（開源版用單一 ref 標記，不埋 campaign UTM）
        self.assertIn("peakstargroup.com/?ref=dataready", html_txt)
        self.assertNotIn("utm_", html_txt)
        # JSON 可解析且結構正確
        data = json.loads(json_txt)
        self.assertEqual(data["tool"], "dataready")
        self.assertEqual(len(data["dimensions"]), 6)
        self.assertIn("consult_url", data)

    def test_english_report(self):
        report = self._report(self.clean)
        html_txt = report_mod.to_html(report, "en")
        self.assertIn("Data Readiness Report", html_txt)
        self.assertNotIn("—", html_txt)

    def test_empty_folder(self):
        empty = self.root / "empty"
        empty.mkdir()
        self.assertEqual(collect.walk(empty), [])


if __name__ == "__main__":
    unittest.main()
