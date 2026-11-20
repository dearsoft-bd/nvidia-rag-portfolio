import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rag_cli import load_dotenv


class DotEnvTests(unittest.TestCase):
    def test_loads_quoted_values_and_preserves_existing_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                'EXAMPLE_MODEL="catalog/model"\n'
                "EXAMPLE_EXISTING=new-value\n"
                "# ignored comment\n",
                encoding="utf-8",
            )
            with patch.dict(
                os.environ,
                {"EXAMPLE_EXISTING": "original-value"},
                clear=False,
            ):
                load_dotenv(env_file)
                self.assertEqual(os.environ["EXAMPLE_MODEL"], "catalog/model")
                self.assertEqual(os.environ["EXAMPLE_EXISTING"], "original-value")


if __name__ == "__main__":
    unittest.main()
