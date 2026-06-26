import time
import unittest
from pathlib import Path

from peakstar_dataready import rules
from peakstar_dataready.analyze import build_report
from peakstar_dataready.extract import FileInfo


def mk(name, **kw):
    base = dict(path=Path(name), ext=Path(name).suffix.lower(), size=100,
                mtime=time.time(), supported=True, extractable=True,
                text="# H\n\nbody paragraph that is reasonably long.\n\nsecond paragraph.",
                char_count=80)
    base.update(kw)
    fi = FileInfo(path=base.pop("path"), ext=base.pop("ext"),
                  size=base.pop("size"), mtime=base.pop("mtime"))
    for k, v in base.items():
        setattr(fi, k, v)
    return fi


class TestScoring(unittest.TestCase):
    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(rules.WEIGHTS.values()), 1.0, places=6)

    def test_light_thresholds(self):
        self.assertEqual(rules.light_for(90), "green")
        self.assertEqual(rules.light_for(65), "yellow")
        self.assertEqual(rules.light_for(30), "red")

    def test_failure_rate_monotonic(self):
        self.assertGreater(rules.expected_failure_rate(20),
                           rules.expected_failure_rate(90))

    def test_extractability_penalizes_scanned(self):
        good = [mk("a.md", content_hash="h1"), mk("b.md", content_hash="h2")]
        bad = [mk("a.md", content_hash="h1"),
               mk("s.pdf", ext=".pdf", extractable=False, is_scanned_pdf=True,
                  text="", char_count=0)]
        rg = build_report(good, "g")
        rb = build_report(bad, "b")
        dg = {d.key: d.score for d in rg.dimensions}
        db = {d.key: d.score for d in rb.dimensions}
        self.assertGreater(dg["extractability"], db["extractability"])

    def test_duplicates_lower_redundancy(self):
        uniq = [mk("a.md", content_hash="h1"), mk("b.md", content_hash="h2")]
        dup = [mk("a.md", content_hash="h1"), mk("b.md", content_hash="h1")]
        du = {d.key: d.score for d in build_report(uniq, "u").dimensions}
        dd = {d.key: d.score for d in build_report(dup, "d").dimensions}
        self.assertGreater(du["redundancy"], dd["redundancy"])

    def test_stale_lowers_freshness(self):
        now = time.time()
        fresh = [mk("a.md", mtime=now, content_hash="h1")]
        old = [mk("a.md", mtime=now - 2000 * 86400, content_hash="h1")]
        df = {d.key: d.score for d in build_report(fresh, "f", now=now).dimensions}
        do = {d.key: d.score for d in build_report(old, "o", now=now).dimensions}
        self.assertGreater(df["freshness"], do["freshness"])

    def test_scanned_pdf_creates_finding(self):
        files = [mk("s1.pdf", ext=".pdf", extractable=False, is_scanned_pdf=True,
                    text="", char_count=0)]
        codes = {f["code"] for f in build_report(files, "x").findings}
        self.assertIn("SCANNED_PDF", codes)

    def test_empty_supported_returns_zero(self):
        files = [mk("a.zip", ext=".zip", supported=False, extractable=False)]
        r = build_report(files, "x")
        self.assertEqual(r.supported_count, 0)
        self.assertEqual(r.total_score, 0.0)
        self.assertEqual(r.light, "red")


if __name__ == "__main__":
    unittest.main()
