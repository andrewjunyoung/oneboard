#!/usr/bin/env python3
"""Repo sanity tests. Run with: python3 tests/test.py"""
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KEYLAYOUTS = [
    ROOT / "iso_odvorak.keylayout",
    ROOT / "src/oracle/iso_odvorak.keylayout",
]

CHAR_DB = ROOT / "src/oracle/data/char_db.csv"
EXPECTED_CHAR_DB_ROWS = 24411


def parse_keylayout(path):
    # Keylayouts are XML 1.1 and use control-character refs (&#x0008; etc.)
    # that XML 1.0 parsers reject, so swap those for a placeholder first.
    text = path.read_text(encoding="utf-8")
    text = text.replace('<?xml version="1.1"', '<?xml version="1.0"', 1)
    def ref(m):
        s = m.group(1)
        cp = int(s[1:], 16) if s[0] in "xX" else int(s)
        return "" if cp < 0x20 or cp == 0x7F else m.group(0)
    text = re.sub(r"&#([xX][0-9A-Fa-f]+|\d+);", ref, text)
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, count=1)
    return ET.fromstring(text)


class KeylayoutStructureTest(unittest.TestCase):
    """Static checks for the things that make macOS silently reject a layout."""

    def check(self, path):
        root = parse_keylayout(path)
        self.assertEqual(root.tag, "keyboard")

        modifier_ids = {m.get("id") for m in root.iter("modifierMap")}
        keymapset_ids = [k.get("id") for k in root.iter("keyMapSet")]
        self.assertEqual(len(keymapset_ids), len(set(keymapset_ids)), "duplicate keyMapSet id")

        for layout in root.iter("layout"):
            self.assertIn(layout.get("mapSet"), keymapset_ids, "layout references unknown mapSet")
            self.assertIn(layout.get("modifiers"), modifier_ids, "layout references unknown modifierMap")

        for mm in root.iter("modifierMap"):
            indexes = [s.get("mapIndex") for s in mm.iter("keyMapSelect")]
            self.assertEqual(len(indexes), len(set(indexes)), f"duplicate keyMapSelect in {mm.get('id')}")
            self.assertIn(mm.get("defaultIndex"), indexes, f"defaultIndex missing in {mm.get('id')}")

        actions = list(root.iter("action"))
        action_ids = [a.get("id") for a in actions]
        dupes = [a for a, n in Counter(action_ids).items() if n > 1]
        self.assertFalse(dupes, f"duplicate action ids: {dupes[:10]}")
        action_ids = set(action_ids)

        maxout = int(root.get("maxout", "0"))
        too_long = []

        for kms in root.iter("keyMapSet"):
            km_indexes = [k.get("index") for k in kms.iter("keyMap")]
            self.assertEqual(len(km_indexes), len(set(km_indexes)),
                             f"duplicate keyMap index in {kms.get('id')}")
            for km in kms.iter("keyMap"):
                codes = [k.get("code") for k in km.iter("key")]
                dup_codes = [c for c, n in Counter(codes).items() if n > 1]
                self.assertFalse(dup_codes, f"duplicate key codes in keyMap {km.get('index')}: {dup_codes}")
                for key in km.iter("key"):
                    has_out = key.get("output") is not None
                    has_act = key.get("action") is not None
                    has_inline = key.find("action") is not None
                    self.assertEqual(has_out + has_act + has_inline, 1,
                                     f"key {key.get('code')} in keyMap {km.get('index')} needs exactly one of output/action")
                    if has_act:
                        self.assertIn(key.get("action"), action_ids,
                                      f"key {key.get('code')} references missing action {key.get('action')!r}")
                    if has_out and len(key.get("output")) > maxout:
                        too_long.append(key.get("output"))

        for action in actions:
            states = [w.get("state") for w in action.iter("when")]
            dup_states = [s for s, n in Counter(states).items() if n > 1]
            self.assertFalse(dup_states, f"action {action.get('id')!r} has duplicate when-states {dup_states}")
            for w in action.iter("when"):
                self.assertTrue(w.get("output") is not None or w.get("next") is not None,
                                f"action {action.get('id')!r} when {w.get('state')!r} has no output/next")
                if w.get("output") is not None and len(w.get("output")) > maxout:
                    too_long.append(w.get("output"))
        self.assertFalse(too_long, f"outputs longer than maxout={maxout}: {too_long[:10]}")

        terminators = [w.get("state") for t in root.iter("terminators") for w in t.iter("when")]
        dup_terms = [s for s, n in Counter(terminators).items() if n > 1]
        self.assertFalse(dup_terms, f"duplicate terminator states: {dup_terms}")

    def test_keylayouts(self):
        for path in KEYLAYOUTS:
            with self.subTest(keylayout=str(path.relative_to(ROOT))):
                self.check(path)


TIS_PROBE = r"""
import Carbon
let list = TISCreateInputSourceList(nil, true).takeRetainedValue() as! [TISInputSource]
for src in list {
    if let p = TISGetInputSourceProperty(src, kTISPropertyInputSourceID) {
        print(Unmanaged<CFString>.fromOpaque(p).takeUnretainedValue())
    }
}
"""


@unittest.skipUnless(sys.platform == "darwin" and shutil.which("swift"), "needs macOS + swift")
@unittest.skipIf(os.environ.get("SKIP_TIS"), "SKIP_TIS set")
class KeylayoutMacOSLoadTest(unittest.TestCase):
    """Installs a uniquely-named copy into ~/Library/Keyboard Layouts and checks
    macOS registers it. macOS drops unparseable layouts silently, so absence = rejected."""

    def probe(self, path):
        name = f"OneboardTest{os.getpid()}"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r'(<keyboard\b[^>]*?)\bid="-?\d+"', r'\1id="-%d"' % (20000 + os.getpid() % 9000), text, count=1)
        text = re.sub(r'(<keyboard\b[^>]*?)\bname="[^"]*"', r'\1name="%s"' % name, text, count=1)

        dest_dir = Path.home() / "Library/Keyboard Layouts"
        dest = dest_dir / f"{name}.keylayout"
        expected_id = f"org.unknown.keylayout.{name}"
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "probe.swift"
            script.write_text(TIS_PROBE)
            try:
                dest.write_text(text, encoding="utf-8")
                found = False
                for _ in range(10):
                    out = subprocess.run(["swift", str(script)], capture_output=True, text=True, timeout=120)
                    self.assertEqual(out.returncode, 0, out.stderr)
                    if expected_id in out.stdout.split():
                        found = True
                        break
                    time.sleep(1)
                self.assertTrue(found, f"macOS did not register {path.name} (rejected as invalid)")
            finally:
                dest.unlink(missing_ok=True)

    def test_keylayouts_load(self):
        for path in KEYLAYOUTS:
            with self.subTest(keylayout=str(path.relative_to(ROOT))):
                self.probe(path)


class CharDbTest(unittest.TestCase):
    def test_row_count(self):
        with open(CHAR_DB, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), EXPECTED_CHAR_DB_ROWS)
        chars = [r["character"] for r in rows]
        self.assertEqual(len(set(chars)), len(chars), "duplicate characters in char_db")


if __name__ == "__main__":
    unittest.main(verbosity=2)
