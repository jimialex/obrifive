import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("build_template", ROOT / "scripts/build_template.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class BuildTemplateTests(unittest.TestCase):
    def test_mirror_identity_survives_rendering_and_branding_still_changes(self):
        config = builder.load_config(ROOT)
        source = (
            "Start Obrifive with gh:Llamitai/saas-bootstrap-template; "
            "run obrifive-api.\n"
        )

        template, changed = builder.templatize_text(
            source, config["tokens"], config["preserve_literals"]
        )

        self.assertTrue(changed)
        self.assertIn("gh:Llamitai/saas-bootstrap-template", template)
        self.assertIn("[[ project_name ]]", template)
        self.assertIn("[[ project_slug ]]-api", template)

    def test_leftover_check_allows_only_the_preserved_mirror_identity(self):
        config = builder.load_config(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            rendered = Path(directory)
            readme = rendered / "README.md"
            readme.write_text("gh:Llamitai/saas-bootstrap-template\n", encoding="utf-8")
            self.assertEqual(builder.check_leftovers(rendered, config, "owner@obrifive.com"), [])

            readme.write_text(
                "gh:Llamitai/saas-bootstrap-template\nObrifive\n", encoding="utf-8"
            )
            problems = builder.check_leftovers(rendered, config, "owner@obrifive.com")
            self.assertEqual(len(problems), 1)
            self.assertIn("README.md:2", problems[0])


if __name__ == "__main__":
    unittest.main()
