from pathlib import Path

import pytest

from vira.business_plan.parser import SUPPORTED_EXTENSIONS, summarise_sections, UnsupportedFormatError


def test_summarise_sections_groups_text():
    text = """Problem: We solve X\nSolution: We do Y\nMarket: Big."""
    sections = summarise_sections(text)
    assert sections["problem"].startswith("Problem")
    assert "Solution" in sections["solution"]


def test_unsupported_extension_raises(tmp_path: Path):
    file_path = tmp_path / "plan.xls"
    file_path.write_bytes(b"")
    with pytest.raises(UnsupportedFormatError):
        from vira.business_plan.parser import extract_text

        extract_text(file_path)

