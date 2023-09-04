from gwdc_python.files.constants import JobType

from gwcloud_python.utils.file_download import (
    _get_endpoint_from_uploaded,
    _download_files,
    _get_file_map_fn,
    _save_file_map_fn, ExternalFileDownloadException
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
def test_file_output_paths():
    return [
        'test_output_path_1',
        'test_output_path_2',
        'test_output_path_3',
        'test_output_path_4',
    ]


@pytest.fixture
def test_job_type():
    return [
        JobType.NORMAL_JOB,
        JobType.NORMAL_JOB,
        JobType.UPLOADED_JOB,
        JobType.UPLOADED_JOB,
        JobType.EXTERNAL_JOB,
        JobType.EXTERNAL_JOB
    ]


@pytest.fixture
def setup_file_download(requests_mock):
    def mock_file_download(test_id, test_path, job_type, test_content):
        test_file = TemporaryFile()
        test_file.write(test_content)
        test_file.seek(0)

        requests_mock.get(_get_endpoint_from_uploaded(job_type) + test_id, body=test_file)

    return mock_file_download


def test_get_endpoint_from_uploaded():
    assert _get_endpoint_from_uploaded(True) == GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT
    assert _get_endpoint_from_uploaded(False) == GWCLOUD_FILE_DOWNLOAD_ENDPOINT


def test_download_files(mocker, test_file_ids, test_file_output_paths, test_file_paths, test_job_type):
    mock_map_fn = mocker.Mock()
    mock_progress = mocker.patch('gwcloud_python.utils.file_download.tqdm')

    _download_files(mock_map_fn, test_file_ids, test_file_output_paths, test_file_paths, test_job_type, 100)
    mock_calls = [
        mocker.call(test_id, test_output_path, test_path, job_type, progress_bar=mock_progress())
        for test_id, test_output_path, test_path, job_type in
        zip(test_file_ids, test_file_output_paths, test_file_paths, test_job_type)
    ]

    mock_map_fn.assert_has_calls(mock_calls)


def test_get_file_map_fn(setup_file_download, mocker):
    test_id = 'test_id'
    test_path = 'test_path'
    test_content = b'Test file content'
    for job_type in [JobType.NORMAL_JOB, JobType.UPLOADED_JOB]:
        setup_file_download(test_id, test_path, job_type, test_content)
        _, file_data = _get_file_map_fn(
            file_id=test_id,
            file_path=test_path,
            job_type=job_type,
            progress_bar=mocker.Mock(),
        )

        assert file_data == test_content


def test_get_file_map_fn_external(setup_file_download, mocker):
    test_id = 'test_id'
    test_path = 'https://aurl.com/myfile.h5?download=1'
    job_type = JobType.EXTERNAL_JOB

    with pytest.raises(ExternalFileDownloadException):
        _get_file_map_fn(
            file_id=test_id,
            file_path=test_path,
            job_type=job_type,
            progress_bar=mocker.Mock(),
        )


def test_save_file_map_fn(setup_file_download, mocker):
    with TemporaryDirectory() as tmp_dir:
        test_id = 'test_id'
        test_path = Path(tmp_dir) / 'test_path'
        test_content = b'Test file content'
        for job_type in [JobType.NORMAL_JOB, JobType.UPLOADED_JOB]:
            setup_file_download(test_id, test_path, job_type, test_content)
            _save_file_map_fn(
                file_id=test_id,
                output_path=test_path,
                file_path=test_path,
                job_type=job_type,
                progress_bar=mocker.Mock(),
            )

            with open(test_path, 'rb') as f:
                file_data = f.read()
                assert file_data == test_content


def test_save_file_map_fn_gwosc(setup_file_download, mocker):
    with TemporaryDirectory() as tmp_dir:
        test_id = 'test_id'
        test_path = 'https://aurl.com/myfile.h5?download=1'
        test_output_path = Path(tmp_dir) / 'test_path'
        job_type = JobType.EXTERNAL_JOB
        with pytest.raises(ExternalFileDownloadException):
            _save_file_map_fn(
                file_id=test_id,
                output_path=test_output_path,
                file_path=test_path,
                job_type=job_type,
                progress_bar=mocker.Mock(),
            )
