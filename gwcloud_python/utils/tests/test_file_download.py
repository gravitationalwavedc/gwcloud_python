from gwdc_python.files import FileReference, FileReferenceList
from gwdc_python.files.constants import GWDCObjectType

from gwcloud_python import BilbyJob
from gwcloud_python.exceptions import ExternalFileDownloadException
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
    ]


@pytest.fixture
def mock_bilby_job(mocker):
    def _mock_bilby_job(i, _type):
        job = BilbyJob(
            client=mocker.Mock(),
            job_id=f'id{i}',
            name='TestName',
            description='Test description',
            user='Test User',
            event_id={'event_id': 'GW123456'},
            job_status={
                'name': 'Completed',
                'date': '2021-12-02'
            },
        )
        job.type = _type
        return job
    return _mock_bilby_job


@pytest.fixture
def test_files(mock_bilby_job):
    return FileReferenceList([
        FileReference(
            path=f'https://aurl.com/myfile.h5?download={i}' if job_type == GWDCObjectType else f'test_path_{i}',
            file_size=None if job_type == GWDCObjectType.EXTERNAL else '1',
            download_token=f'test_token_{i}',
            parent=mock_bilby_job(i, job_type)
        )
        for i, job_type in enumerate([GWDCObjectType.NORMAL, GWDCObjectType.UPLOADED, GWDCObjectType.EXTERNAL])
    ])


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


def test_download_files(mocker, test_file_ids, test_files):
    mock_map_fn = mocker.Mock()
    mock_progress = mocker.patch('gwcloud_python.utils.file_download.tqdm')

    _download_files(mock_map_fn, test_file_ids, test_files)
    mock_calls = [
        mocker.call(test_id, test_file, progress_bar=mock_progress(), root_path=None)
        for test_id, test_file in zip(test_file_ids, test_files)
    ]

    mock_map_fn.assert_has_calls(mock_calls)


def test_get_file_map_fn(setup_file_download, test_files, mocker):
    test_id = 'test_id'
    test_content = b'Test file content'
    for ref in test_files[:2]:
        setup_file_download(test_id, ref.path, ref.parent.is_uploaded(), test_content)
        _, file_data = _get_file_map_fn(
            file_id=test_id,
            file_ref=ref,
            progress_bar=mocker.Mock(),
        )

        assert file_data == test_content


def test_get_file_map_fn_external(setup_file_download, test_files, mocker):
    test_id = 'test_id'
    with pytest.raises(ExternalFileDownloadException):
        _get_file_map_fn(
            file_id=test_id,
            file_ref=test_files[2],
            progress_bar=mocker.Mock(),
        )


def test_save_file_map_fn(setup_file_download, test_files, mocker):
    with TemporaryDirectory() as tmp_dir:
        test_id = 'test_id'
        root_path = Path(tmp_dir)
        test_content = b'Test file content'
        for ref in test_files[:2]:
            setup_file_download(test_id, root_path / ref.path, ref.parent.is_uploaded(), test_content)
            _save_file_map_fn(
                file_id=test_id,
                file_ref=ref,
                root_path=root_path,
                progress_bar=mocker.Mock(),
            )

            with open(root_path / ref.path, 'rb') as f:
                file_data = f.read()
                assert file_data == test_content


def test_save_file_map_fn_gwosc(setup_file_download, test_files, mocker):
    with TemporaryDirectory() as tmp_dir:
        test_id = 'test_id'
        root_path = Path(tmp_dir)
        with pytest.raises(ExternalFileDownloadException):
            _save_file_map_fn(
                file_id=test_id,
                file_ref=test_files[2],
                root_path=root_path,
                progress_bar=mocker.Mock(),
            )
