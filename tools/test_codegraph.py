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


    def test_endpoint_for_prefers_the_literal_path(self):
        eps = [("m.py", 1, "GET", "/api/countries/{name}", "country"), ("m.py", 2, "GET", "/api/countries.csv", "csv")]
        self.assertEqual(cg.endpoint_for(eps, "/api/countries/Peru")[4], "country")
        self.assertEqual(cg.endpoint_for(eps, "/api/countries.csv")[4], "csv")
        self.assertIsNone(cg.endpoint_for(eps, "/api/plants"))

    def test_flow_tree_follows_a_route_to_its_tables_and_tests(self):
        nodes = {
            "route:/": ("route", "/", "App.tsx:1"), "page:Home": ("page", "Home", "Home.tsx:1"),
            "component:Table": ("component", "Table", ""), "api:listApi": ("api", "listApi", "api.ts:3"),
            "endpoint:GET /api/list": ("endpoint", "GET /api/list", "main.py:9"), "table:items": ("table", "items", ""),
            "test:test_list": ("test", "test_list", "test.py:4"),
        }
        edges = [
            ("route:/", "shows", "page:Home"), ("page:Home", "renders", "component:Table"),
            ("component:Table", "calls", "api:listApi"), ("api:listApi", "requests", "endpoint:GET /api/list"),
            ("endpoint:GET /api/list", "reads", "table:items"), ("test:test_list", "tests", "endpoint:GET /api/list"),
        ]
        self.assertEqual(cg.flow_tree(nodes, edges), [
            "/  ->  Home  (Home.tsx:1)",
            "├── renders  Table",
            "└── listApi  (via Table)",
            "    └── GET /api/list  (main.py:9)",
            "        ├── reads  items",
            "        └── tests  test_list",
            "",
        ])


if __name__ == "__main__":
    unittest.main()
