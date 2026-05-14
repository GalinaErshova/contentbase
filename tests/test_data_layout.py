"""Тесты соглашений по директориям с данными."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUTOTEST_DATA_DIR = REPO_ROOT / "data" / "raw"
SUBMISSION_DATA_DIR = REPO_ROOT / "data" / "project1"


def test_raw_directory_contains_autotest_fixtures():
    """`data/raw` хранит стабильные маленькие файлы для автотестов и демо-команд."""
    assert AUTOTEST_DATA_DIR.is_dir()

    fixture_files = sorted(AUTOTEST_DATA_DIR.glob("sample_*.md"))

    assert fixture_files
    assert {file.name for file in fixture_files} >= {
        "sample_01_rag.md",
        "sample_02_llmops.md",
    }


def test_project1_directory_is_reserved_for_submission_files():
    """`data/project1` зарезервирована для пользовательских файлов сдачи."""
    assert SUBMISSION_DATA_DIR.is_dir()
    assert SUBMISSION_DATA_DIR != AUTOTEST_DATA_DIR

    submission_files = [
        file_path
        for file_path in SUBMISSION_DATA_DIR.rglob("*")
        if file_path.is_file() and not file_path.name.endswith(":Zone.Identifier")
    ]

    assert submission_files
