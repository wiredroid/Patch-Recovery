#!/usr/bin/env python3
"""Unit tests use SYNTHETIC CRCs only; never represent actual OEM evidence."""
import importlib.util
from pathlib import Path
import unittest

module_path = Path(__file__).with_name("compare-oem-vendor-module-crcs.py")
spec = importlib.util.spec_from_file_location("a146p_crc_compare", module_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class VendorCRCAudit(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            {"symbol": "good", "module_crc": "0x00000001", "status": "RESEARCH"},
            {"symbol": "bad", "module_crc": "0x00000002", "status": "RESEARCH"},
            {"symbol": "conflict", "module_crc": "0x00000003", "status": "RESEARCH"},
            {"symbol": "absent", "module_crc": "", "status": "RESEARCH"},
        ]
        self.evidence = {
            "expected_release": mod.EXPECTED,
            "matching_release_modules": [{"file": "SYNTHETIC-A.ko", "symbol_count": 3}],
            "conflicting_symbols": {
                "conflict": [{"crc": "0x00000003"}, {"crc": "0x00000004"}]
            },
            "symbols": {
                "good": {"crcs": ["0x1"], "module_names": ["SYNTHETIC-A.ko"]},
                "bad": {"crcs": ["0x5"], "module_names": ["SYNTHETIC-A.ko"]},
                "conflict": {"crcs": ["0x3", "0x4"], "module_names": ["SYNTHETIC-A.ko"]},
            },
        }

    def test_classification_and_explicit_no_load(self):
        summary, rows = mod.inspect(self.candidates, self.evidence)
        self.assertEqual([r["comparison"] for r in rows], [
            "MATCH_TO_INSTALLED_MODULE_REFERENCE_NOT_OEM_PROOF",
            "MISMATCH_TO_INSTALLED_MODULE_REFERENCE",
            "REFERENCE_CRC_CONFLICT",
            "NO_EXACT_RELEASE_REFERENCE",
        ])
        self.assertEqual(summary["candidate_import_count"], 4)
        self.assertFalse(summary["oem_crc_verified"])
        self.assertFalse(summary["ready_to_load"])
        self.assertFalse(summary["factory_locked_root_demonstrated"])

    def test_wrong_release_rejected(self):
        self.evidence["expected_release"] = "6.6.50"
        with self.assertRaisesRegex(ValueError, "different kernel release"):
            mod.inspect(self.candidates, self.evidence)

    def test_zero_matching_modules_rejected(self):
        self.evidence["matching_release_modules"] = []
        with self.assertRaisesRegex(ValueError, "no installed modules"):
            mod.inspect(self.candidates, self.evidence)

    def test_multi_crc_conflict_flagged(self):
        self.evidence["symbols"]["good"]["crcs"] = ["0x1", "0x9"]
        _, rows = mod.inspect(self.candidates, self.evidence)
        self.assertEqual(rows[0]["comparison"], "REFERENCE_CRC_CONFLICT")

    def test_bad_crc_strings_rejected(self):
        self.assertEqual(mod.normalize_crc("0xF"), "0x0000000f")
        for bad in ["F", "0xGG", "0x123456789", "", "-0x1", None]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                mod.normalize_crc(bad)


if __name__ == "__main__":
    unittest.main()
