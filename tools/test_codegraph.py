import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import codegraph as cg

TS = """export function A({ a }: { a: string }) {
  return `${a}}`
}
export type T =
  | 'x'
  | 'y'
const u = '/api/x'
"""


class CodegraphTest(unittest.TestCase):
    def test_ts_declaration_ranges(self):
        self.assertEqual(
            cg.ts_symbols(TS),
            [("A", "function", 1, 3), ("T", "type", 4, 6), ("u", "const", 7, 7)],
        )

    def test_python_symbol_starts_at_the_decorator(self):
        tree = cg.ast.parse("@d\ndef f():\n    pass\n")
        self.assertEqual(cg.py_symbols(tree), [("f", "function", 1, 3)])

    def test_sql_view_reads_belong_to_the_view(self):
        hits = list(cg.sql_hits("CREATE VIEW v AS SELECT 1 FROM t JOIN u ON 1"))
        self.assertEqual([(h[1], h[2], h[3]) for h in hits], [(None, "define", "v"), ("v", "read", "t"), ("v", "read", "u")])


if __name__ == "__main__":
    unittest.main()
