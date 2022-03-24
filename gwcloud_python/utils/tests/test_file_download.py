from gwcloud_python.utils.file_download import (
    _get_endpoint_from_uploaded,
    _download_files,
    _get_file_map_fn,
    _save_file_map_fn
)
from gwcloud_python.settings import GWCLOUD_FILE_DOWNLOAD_ENDPOINT, GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT
import pytest
from tempfile import TemporaryFile, TemporaryDirectory
from pathlib import Path


@pytest.fixture
def test_file_ids():
    return [
        'test_id_1',
        'test_id_2',
        'test_id_3',
        'test_id_4',
    ]


@pytest.fixture
def test_file_paths():
    return [
        'test_path_1',
        'test_path_2',
        'test_path_3',
        'test_path_4',
    ]


@pytest.fixture
def test_file_uploaded():
    return [
        False,
        False,
        True,
        True,
    ]


@pytest.fixture
def setup_file_download(requests_mock):
    def mock_file_download(test_id, test_path, test_uploaded, test_content):
        test_file = TemporaryFile()
        test_file.write(test_content)
        test_file.seek(0)

        requests_mock.get(_get_endpoint_from_uploaded(test_uploaded) + test_id, body=test_file)
    return mock_file_download


def test_get_endpoint_from_uploaded():
    assert _get_endpoint_from_uploaded(True) == GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT
    assert _get_endpoint_from_uploaded(False) == GWCLOUD_FILE_DOWNLOAD_ENDPOINT


def test_download_files(mocker, test_file_ids, test_file_paths, test_file_uploaded):
    mock_map_fn = mocker.Mock()
    mock_progress = mocker.patch('gwcloud_python.utils.file_download.tqdm')

    _download_files(mock_map_fn, test_file_ids, test_file_paths, test_file_uploaded, 100)
    mock_calls = [
            mocker.call(test_id, test_path, test_uploaded, progress_bar=mock_progress())
            for test_id, test_path, test_uploaded in zip(test_file_ids, test_file_paths, test_file_uploaded)
        ]

    mock_map_fn.assert_has_calls(mock_calls)


def test_get_file_map_fn(setup_file_download, mocker):
    test_id = 'test_id'
    test_path = 'test_path'
    test_uploaded = False
    test_content = b'Test file content'
    setup_file_download(test_id, test_path, test_uploaded, test_content)
    _, file_data = _get_file_map_fn(
        file_id=test_id,
        file_path=test_path,
        file_uploaded=test_uploaded,
        progress_bar=mocker.Mock(),
    )

    assert file_data == test_content


def test_save_file_map_fn(setup_file_download, mocker):
    with TemporaryDirectory() as tmp_dir:
        test_id = 'test_id'
        test_path = Path(tmp_dir) / 'test_path'
        test_uploaded = False
        test_content = b'Test file content'
        setup_file_download(test_id, test_path, test_uploaded, test_content)
        _save_file_map_fn(
            file_id=test_id,
            file_path=test_path,
            file_uploaded=test_uploaded,
            progress_bar=mocker.Mock(),
        )

        with open(test_path, 'rb') as f:
            file_data = f.read()
            assert file_data == test_content
