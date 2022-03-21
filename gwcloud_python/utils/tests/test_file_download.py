from gwcloud_python.utils.file_download import _download_files, GWCLOUD_FILE_DOWNLOAD_ENDPOINT
import pytest


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


def test_download_files(mocker, test_file_ids, test_file_paths):
    mock_map_fn = mocker.Mock()
    mock_progress = mocker.patch('gwcloud_python.utils.file_download.tqdm')

    _download_files(mock_map_fn, test_file_ids, test_file_paths, 100, False)
    mock_calls = [
            mocker.call(test_id, test_path, progress_bar=mock_progress(), endpoint=GWCLOUD_FILE_DOWNLOAD_ENDPOINT)
            for test_id, test_path in zip(test_file_ids, test_file_paths)
        ]

    mock_map_fn.assert_has_calls(mock_calls)
