"""Қабаттар шекарасын тексереді: деңгейлер бір-біріне тек рұқсат етілген бағытта тәуелді."""
import os
import re
import unittest

SRC = os.path.join(os.path.dirname(__file__), "..", "src")

# қай қабат қандай модульдерді импорттай алмайды
FORBIDDEN = {
    "presentation": ["data", "pyodbc"],                      # UI дерекқорға тікелей шықпайды
    "business": ["flask", "pyodbc", "data", "presentation"], # логика Flask пен SQL-ді білмейді
    "data": ["flask", "business", "presentation"],           # деректер деңгейі жоғарғы қабаттарды білмейді
}
IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][\w]*)", re.M)


class ArchitectureTests(unittest.TestCase):
    def test_layer_dependencies(self):
        problems = []
        for layer, banned in FORBIDDEN.items():
            folder = os.path.join(SRC, layer)
            for name in os.listdir(folder):
                if not name.endswith(".py"):
                    continue
                with open(os.path.join(folder, name), encoding="utf-8") as f:
                    imported = set(IMPORT_RE.findall(f.read()))
                for module in imported & set(banned):
                    problems.append(f"{layer}/{name} -> {module}")
        self.assertEqual(problems, [], "Қабат шекарасы бұзылған: " + ", ".join(problems))


if __name__ == "__main__":
    unittest.main()
