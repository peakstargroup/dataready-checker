import tempfile
import unittest
from pathlib import Path

from peakstar_dataready.extract import analyze_file
from tests import helpers as h


class TestExtract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_markdown_headings(self):
        p = h.write_text(self.d, "a.md", "# H1\n\ntext\n\n## H2\n\nmore")
        f = analyze_file(p)
        self.assertTrue(f.extractable)
        self.assertEqual(f.heading_count, 2)

    def test_csv_consistency(self):
        good = analyze_file(h.write_text(self.d, "g.csv", "a,b,c\n1,2,3\n4,5,6"))
        bad = analyze_file(h.write_text(self.d, "b.csv", "a,b\n1,2,3\n4"))
        self.assertTrue(good.csv_consistent)
        self.assertFalse(bad.csv_consistent)

    def test_docx(self):
        p = h.write_bytes(self.d, "d.docx", h.docx_bytes(headings=2))
        f = analyze_file(p)
        self.assertTrue(f.extractable)
        self.assertEqual(f.heading_count, 2)
        self.assertIn("Body paragraph", f.text)

    def test_xlsx_merged(self):
        f = analyze_file(h.write_bytes(self.d, "x.xlsx", h.xlsx_bytes(merged=2)))
        self.assertTrue(f.extractable)
        self.assertEqual(f.merged_cells, 2)

    def test_pptx_pages(self):
        f = analyze_file(h.write_bytes(self.d, "p.pptx", h.pptx_bytes(["a", "b", "c"])))
        self.assertTrue(f.extractable)
        self.assertEqual(f.pages, 3)

    def test_html_headings(self):
        f = analyze_file(h.write_text(self.d, "p.html", h.html_text(headings=3)))
        self.assertEqual(f.heading_count, 3)

    def test_pdf_text_extractable(self):
        f = analyze_file(h.write_bytes(self.d, "t.pdf", h.pdf_text_bytes()))
        self.assertTrue(f.extractable)
        self.assertFalse(f.is_scanned_pdf)
        self.assertGreater(f.char_count, 0)
        self.assertGreaterEqual(f.pages, 1)

    def test_pdf_scanned_detected(self):
        f = analyze_file(h.write_bytes(self.d, "s.pdf", h.pdf_scanned_bytes()))
        self.assertFalse(f.extractable)
        self.assertTrue(f.is_scanned_pdf)

    def test_pdf_pathological_is_fast(self):
        # 回歸鎖定：舊的巢狀正則在這種內容流上會 O(n²) 爆炸（256KB 即 >80s）。
        # 線性解析器必須在亞秒級完成；給 5s 寬裕上限避免 CI 抖動誤判。
        import time
        p = h.write_bytes(self.d, "pathological.pdf", h.pdf_pathological_bytes(2))
        t = time.perf_counter()
        f = analyze_file(p)
        elapsed = time.perf_counter() - t
        self.assertLess(elapsed, 5.0, f"PDF 解析過慢（{elapsed:.1f}s），疑似正則回歸")
        self.assertFalse(f.corrupt)

    def test_unsupported_flagged(self):
        f = analyze_file(h.write_bytes(self.d, "a.zip", b"PK junk"))
        self.assertFalse(f.supported)

    def test_corrupt_docx_flagged(self):
        f = analyze_file(h.write_bytes(self.d, "broken.docx", b"not a zip"))
        self.assertTrue(f.corrupt)
        self.assertFalse(f.extractable)

    def test_duplicate_hash_matches(self):
        a = analyze_file(h.write_text(self.d, "a.md", "# T\n\nsame body here"))
        b = analyze_file(h.write_text(self.d, "b.md", "# T\n\nsame body here"))
        self.assertEqual(a.content_hash, b.content_hash)
        self.assertNotEqual(a.content_hash, "")


if __name__ == "__main__":
    unittest.main()
