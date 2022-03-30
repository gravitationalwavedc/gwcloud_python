from gwcloud_python.utils.file_upload import check_file
import pytest
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path


def test_get_endpoint_from_uploaded():
    with TemporaryDirectory() as tmp_dir:
        test_file = NamedTemporaryFile(dir=tmp_dir)
        try:
            file_name = check_file(test_file.name)
            assert file_name == Path(test_file.name)
        except Exception:
            pytest.fail("check_file is failing when it shouldn't")

        with pytest.raises(Exception):
            check_file(tmp_dir / 'nonexistant')
