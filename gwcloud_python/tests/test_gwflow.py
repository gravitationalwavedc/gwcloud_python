import os
import json
import pytest
from datetime import datetime
from tempfile import NamedTemporaryFile

from gwcloud_python import GWCloud
from gwcloud_python.exceptions import GWCloudException
from gwcloud_python.gwflow_pending_file import GWFlowPendingFile
from gwcloud_python.gwflow_job_upsert_result import GWFlowJobUpsertResult
from gwcloud_python.gwflow_job import GWFlowJob
from gwcloud_python.gwflow_file import GWFlowFile
from gwcloud_python.gwflow_linked_bilby_job import GWFlowLinkedBilbyJob
from gwcloud_python.gwflow_event_id import GWFlowEventID

@pytest.fixture
def mock_gwdc_init(mocker):
    def mock_init(self, token, endpoint, custom_error_handler=None):
        pass

    mocker.patch('gwdc_python.gwdc.GWDC.__init__', mock_init)


def test_upsert_gwflow_job_minimal(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'upsert_gwflow_job': {
            'result': {
                'gwflow_job_id': 'job123',
                'sname': 'S230101a',
                'created': True,
                'files_pending': []
            }
        }
    }))
    gwc = GWCloud(token='my_token')
    result = gwc.upsert_gwflow_job('S230101a')
    
    assert isinstance(result, GWFlowJobUpsertResult)
    assert result.job_id == 'job123'
    assert result.sname == 'S230101a'
    assert result.created is True
    assert result.files_pending == []
    
    request_mock = gwc.client.request
    assert request_mock.call_count == 1
    call_args = request_mock.call_args[1]
    assert 'upsertGwflowJob' in call_args['query']
    assert call_args['variables']['input']['params'] == {'sname': 'S230101a'}

def test_upsert_gwflow_job_full(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'upsert_gwflow_job': {
            'result': {
                'gwflow_job_id': 'job123',
                'sname': 'S230101a',
                'created': False,
                'files_pending': [
                    {'id': 'f1', 'sname': 'S230101a', 'analysisUid': 'uid1', 'path': '/p', 'fileName': 'f.txt', 'md5Sum': 'abc'}
                ]
            }
        }
    }))
    gwc = GWCloud(token='my_token')
    dt = datetime(2023, 1, 1, 12, 0, 0)
    
    result = gwc.upsert_gwflow_job(
        'S230101a',
        schema_version='1.0',
        metadata={'key': 'value'},
        libraries=['lib1', 'lib2'],
        is_pruned=False,
        ligo_only=True,
        event_id='GW123',
        current_history_id='hist1',
        current_history_timestamp=dt,
        files=[{'analysis_uid': 'uid1', 'path': '/p', 'file_name': 'f.txt', 'file_size': 100, 'md5_sum': 'abc'}]
    )
    
    assert isinstance(result, GWFlowJobUpsertResult)
    assert len(result.files_pending) == 1
    assert isinstance(result.files_pending[0], GWFlowPendingFile)
    assert result.files_pending[0].id == 'f1'
    assert result.files_pending[0].analysis_uid == 'uid1'
    
    request_mock = gwc.client.request
    call_args = request_mock.call_args[1]
    params = call_args['variables']['input']['params']
    
    assert params['metadata'] == json.dumps({'key': 'value'})
    assert params['currentHistoryTimestamp'] == dt.isoformat()
    assert params['files'] == [
        {'analysisUid': 'uid1', 'path': '/p', 'fileName': 'f.txt', 'fileSize': 100, 'md5Sum': 'abc'}
    ]
    assert params['libraries'] == ['lib1', 'lib2']
    assert params['isPruned'] is False
    assert params['ligoOnly'] is True

@pytest.fixture
def tmp_upload_file():
    """Create a small temporary file for upload tests and clean up afterwards."""
    with NamedTemporaryFile(delete=False) as f:
        f.write(b'test')
        path = f.name
    yield path
    os.unlink(path)


def test_upload_gwflow_file_success(mock_gwdc_init, mocker, tmp_upload_file):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'upload_gwflow_file': {
            'result': {
                'success': True,
                'file_size': 12345
            }
        }
    }))
    gwc = GWCloud(token='my_token')
    size = gwc.upload_gwflow_file('file123', tmp_upload_file)
    assert size == 12345


def test_upload_gwflow_file_error(mock_gwdc_init, mocker, tmp_upload_file):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(side_effect=Exception("GraphQL error")))
    gwc = GWCloud(token='my_token')
    with pytest.raises(Exception, match="GraphQL error"):
        gwc.upload_gwflow_file('file123', tmp_upload_file)


def test_upload_gwflow_file_success_false(mock_gwdc_init, mocker, tmp_upload_file):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'upload_gwflow_file': {
            'result': {
                'success': False,
                'file_size': 0
            }
        }
    }))
    gwc = GWCloud(token='my_token')
    with pytest.raises(Exception, match="Failed to upload GWFlow file."):
        gwc.upload_gwflow_file('file123', tmp_upload_file)


def test_upsert_gwflow_job_zero_file_size(mock_gwdc_init, mocker):
    """Regression: file_size=0 must not be dropped from mutation variables (0 is falsy)."""
    mock_request = mocker.Mock(return_value={
        'upsert_gwflow_job': {
            'result': {
                'gwflow_job_id': 'job1',
                'sname': 'S230101a',
                'created': False,
                'files_pending': []
            }
        }
    })
    mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)
    gwc = GWCloud(token='my_token')
    gwc.upsert_gwflow_job(
        'S230101a',
        files=[{'path': '/p', 'file_name': 'f.txt', 'analysis_uid': 'u1', 'file_size': 0}]
    )
    call_args = mock_request.call_args[1]
    sent_files = call_args['variables']['input']['params']['files']
    assert sent_files[0]['fileSize'] == 0



def test_get_gwflow_pending_files(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'gwflow_pending_files': [
            {'id': 'f1', 'sname': 's1', 'analysisUid': 'u1', 'path': 'p1', 'fileName': 'n1', 'md5Sum': 'm1'},
            {'id': 'f2', 'sname': 's2', 'analysisUid': 'u2', 'path': 'p2', 'fileName': 'n2', 'md5Sum': 'm2'},
        ]
    }))
    gwc = GWCloud(token='my_token')
    
    results = gwc.get_gwflow_pending_files()
    assert len(results) == 2
    assert isinstance(results[0], GWFlowPendingFile)
    assert results[0].id == 'f1'
    assert results[0].analysis_uid == 'u1'
    assert results[1].id == 'f2'

def test_link_bilby_job_to_gwflow_success(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'link_bilby_job_to_gwflow': {
            'result': {
                'success': True
            }
        }
    }))
    gwc = GWCloud(token='my_token')
    gwc.link_bilby_job_to_gwflow('job1', 'S230101a', 'uid1')

def test_link_bilby_job_to_gwflow_error(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'link_bilby_job_to_gwflow': {
            'result': {
                'success': False
            }
        }
    }))
    gwc = GWCloud(token='my_token')
    with pytest.raises(Exception):
        gwc.link_bilby_job_to_gwflow('job1', 'S230101a', 'uid1')

def test_link_bilby_job_to_gwflow_unlink(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'link_bilby_job_to_gwflow': {
            'result': {
                'success': True
            }
        }
    }))
    gwc = GWCloud(token='my_token')
    gwc.link_bilby_job_to_gwflow('job1', '', 'uid1')
    
    request_mock = gwc.client.request
    call_args = request_mock.call_args[1]
    assert call_args['variables']['input']['sname'] == ''


def test_get_gwflow_job_list_paginates(mock_gwdc_init, mocker):
    page1 = {
        'gwflow_jobs': {
            'edges': [
                {'node': {
                    'id': 'job1',
                    'sname': 'S230101a',
                    'schema_version': '1.0',
                    'libraries': ['lib1'],
                    'is_pruned': False,
                    'ligo_only': False,
                    'current_history_id': 'h1',
                    'current_history_timestamp': '2023-01-01T00:00:00',
                    'last_updated': '2023-01-01T00:00:00',
                    'event_id': None
                }, 'cursor': 'cursor1'}
            ],
            'page_info': {'has_next_page': True, 'end_cursor': 'cursor2'}
        }
    }
    page2 = {
        'gwflow_jobs': {
            'edges': [
                {'node': {
                    'id': 'job2',
                    'sname': 'S230102a',
                    'schema_version': '1.0',
                    'libraries': ['lib2'],
                    'is_pruned': False,
                    'ligo_only': False,
                    'current_history_id': 'h2',
                    'current_history_timestamp': '2023-01-02T00:00:00',
                    'last_updated': '2023-01-02T00:00:00',
                    'event_id': None
                }, 'cursor': 'cursor2'}
            ],
            'page_info': {'has_next_page': False, 'end_cursor': None}
        }
    }
    mock_request = mocker.Mock(side_effect=[page1, page2])
    mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)
    gwc = GWCloud(token='my_token')

    jobs = gwc.get_gwflow_job_list()

    assert len(jobs) == 2
    assert all(isinstance(job, GWFlowJob) for job in jobs)
    assert mock_request.call_count == 2
    second_call_args = mock_request.call_args_list[1][1]
    assert second_call_args['variables']['cursor'] == 'cursor2'


def test_get_gwflow_job_list_summary_parsing(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'gwflow_jobs': {
            'edges': [
                {'node': {
                    'id': 'job1',
                    'sname': 'S230101a',
                    'schema_version': '1.0',
                    'libraries': ['lib1'],
                    'is_pruned': True,
                    'ligo_only': True,
                    'current_history_id': 'h1',
                    'current_history_timestamp': '2023-01-01T00:00:00',
                    'last_updated': '2023-01-01T00:00:00',
                    'event_id': None
                }, 'cursor': 'c1'},
                {'node': {
                    'id': 'job2',
                    'sname': 'S230102a',
                    'schema_version': '1.0',
                    'libraries': ['lib2'],
                    'is_pruned': False,
                    'ligo_only': False,
                    'current_history_id': 'h2',
                    'current_history_timestamp': '2023-01-02T00:00:00',
                    'last_updated': '2023-01-02T00:00:00',
                    'event_id': {
                        'event_id': 'evt1',
                        'trigger_id': 'trig1',
                        'nickname': 'nick1',
                        'gps_time': 1234567890.0
                    }
                }, 'cursor': 'c2'}
            ],
            'page_info': {'has_next_page': False, 'end_cursor': None}
        }
    }))
    gwc = GWCloud(token='my_token')

    jobs = gwc.get_gwflow_job_list()

    assert jobs[0].event_id is None
    assert isinstance(jobs[1].event_id, GWFlowEventID)
    assert jobs[1].event_id.event_id == 'evt1'
    assert jobs[1].event_id.trigger_id == 'trig1'
    assert jobs[1].event_id.nickname == 'nick1'
    assert jobs[1].event_id.gps_time == 1234567890.0


def test_get_gwflow_job_detail(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'gwflow_job_by_sname': {
            'id': 'job1',
            'sname': 'S230101a',
            'schema_version': '1.0',
            'libraries': ['lib1'],
            'is_pruned': False,
            'ligo_only': False,
            'current_history_id': 'h1',
            'current_history_timestamp': '2023-01-01T00:00:00',
            'creation_time': '2023-01-01T00:00:00',
            'last_updated': '2023-01-01T00:00:00',
            'event_id': None,
            'files': [
                {'id': 'f1', 'analysis_uid': 'uid1', 'path': '/p1', 'file_name': 'a.txt', 'file_size': 100,
                 'uploaded': True, 'download_token': 'tok1'},
                {'id': 'f2', 'analysis_uid': 'uid2', 'path': '/p2', 'file_name': 'b.txt', 'file_size': 200,
                 'uploaded': False, 'download_token': 'tok2'}
            ],
            'bilby_jobs': [
                {'id': 'bj1', 'name': 'bilby1', 'gwflow_analysis_uid': 'uid1'}
            ]
        }
    }))
    gwc = GWCloud(token='my_token')

    job = gwc.get_gwflow_job('S230101a')

    assert isinstance(job, GWFlowJob)
    assert job.sname == 'S230101a'
    assert len(job.files) == 2
    assert isinstance(job.files[0], GWFlowFile)
    assert job.files[0].id == 'f1'
    assert job.files[0].analysis_uid == 'uid1'
    assert job.files[0].file_name == 'a.txt'
    assert job.files[0].file_size == 100
    assert job.files[0].uploaded is True
    assert job.files[0].download_token == 'tok1'
    assert len(job.bilby_jobs) == 1
    assert isinstance(job.bilby_jobs[0], GWFlowLinkedBilbyJob)
    assert job.bilby_jobs[0].id == 'bj1'
    assert job.bilby_jobs[0].name == 'bilby1'
    assert job.bilby_jobs[0].gwflow_analysis_uid == 'uid1'


def test_get_gwflow_job_not_found(mock_gwdc_init, mocker):
    mocker.patch('gwdc_python.gwdc.GWDC.request', mocker.Mock(return_value={
        'gwflow_job_by_sname': None
    }))
    gwc = GWCloud(token='my_token')

    result = gwc.get_gwflow_job('S230101a')

    assert result is None


def test_download_gwflow_file_success(mock_gwdc_init, mocker, requests_mock, tmp_path):
    requests_mock.get('https://gwcloud.org.au/file_download/?fileId=token123', content=b'test content')
    gwc = GWCloud(token='my_token')
    output_path = tmp_path / 'downloaded.txt'

    gwc.download_gwflow_file('token123', output_path)

    assert output_path.read_bytes() == b'test content'


def test_download_gwflow_file_404(mock_gwdc_init, mocker, requests_mock, tmp_path):
    requests_mock.get('https://gwcloud.org.au/file_download/?fileId=token123', status_code=404)
    gwc = GWCloud(token='my_token')

    with pytest.raises(GWCloudException):
        gwc.download_gwflow_file('token123', tmp_path / 'downloaded.txt')


def test_get_gwflow_job_list_stops_on_none_cursor(mock_gwdc_init, mocker):
    page = {
        'gwflow_jobs': {
            'edges': [
                {'node': {
                    'id': 'job1',
                    'sname': 'S230101a',
                    'schema_version': '1.0',
                    'libraries': [],
                    'is_pruned': False,
                    'ligo_only': False,
                    'current_history_id': 'h1',
                    'current_history_timestamp': '2023-01-01T00:00:00',
                    'last_updated': '2023-01-01T00:00:00',
                    'event_id': None
                }, 'cursor': 'cursor1'}
            ],
            'page_info': {'has_next_page': True, 'end_cursor': None}
        }
    }
    mock_request = mocker.Mock(return_value=page)
    mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)
    gwc = GWCloud(token='my_token')

    jobs = gwc.get_gwflow_job_list()

    assert len(jobs) == 1
    assert mock_request.call_count == 1


def test_get_gwflow_job_list_stops_on_repeated_cursor(mock_gwdc_init, mocker):
    page = {
        'gwflow_jobs': {
            'edges': [
                {'node': {
                    'id': 'job1',
                    'sname': 'S230101a',
                    'schema_version': '1.0',
                    'libraries': [],
                    'is_pruned': False,
                    'ligo_only': False,
                    'current_history_id': 'h1',
                    'current_history_timestamp': '2023-01-01T00:00:00',
                    'last_updated': '2023-01-01T00:00:00',
                    'event_id': None
                }, 'cursor': 'cursor1'}
            ],
            'page_info': {'has_next_page': True, 'end_cursor': 'cursor1'}
        }
    }
    mock_request = mocker.Mock(return_value=page)
    mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)
    gwc = GWCloud(token='my_token')

    jobs = gwc.get_gwflow_job_list()

    assert len(jobs) == 2
    assert mock_request.call_count == 2


def test_gwflow_file_from_dict_preserves_zero_size():
    f = GWFlowFile.from_dict({
        'id': 'f1',
        'analysisUid': 'uid1',
        'path': '/p',
        'fileName': 'a.txt',
        'fileSize': 0,
        'uploaded': True,
        'downloadToken': 'tok1'
    })
    assert f.file_size == 0


def test_gwflow_event_id_from_dict_preserves_zero_gps_time():
    e = GWFlowEventID.from_dict({
        'eventId': 'evt1',
        'triggerId': 'trig1',
        'nickname': 'nick1',
        'gpsTime': 0.0
    })
    assert e.gps_time == 0.0


def test_download_gwflow_file_server_error(mock_gwdc_init, mocker, requests_mock, tmp_path):
    requests_mock.get('https://gwcloud.org.au/file_download/?fileId=token123', status_code=500)
    gwc = GWCloud(token='my_token')

    with pytest.raises(GWCloudException, match="500"):
        gwc.download_gwflow_file('token123', tmp_path / 'downloaded.txt')


def test_gwflow_job_fresh_list_defaults():
    job1 = GWFlowJob(
        id='job1',
        sname='S230101a',
        schema_version='1.0',
        libraries='lib1',
        is_pruned=True,
        ligo_only=True,
        current_history_id='h1',
        current_history_timestamp='2023-01-01T00:00:00',
        last_updated='2023-01-01T00:00:00'
    )
    job2 = GWFlowJob(
        id='job2',
        sname='S230102a',
        schema_version='1.0',
        libraries='lib2',
        is_pruned=False,
        ligo_only=False,
        current_history_id='h2',
        current_history_timestamp='2023-01-02T00:00:00',
        last_updated='2023-01-02T00:00:00'
    )
    assert job1.files is not job2.files
    assert job1.bilby_jobs is not job2.bilby_jobs
    assert job1.files == []
    assert job1.bilby_jobs == []


def test_gwflow_job_dataclass_equality():
    job1 = GWFlowJob(
        id='job1',
        sname='S230101a',
        schema_version='1.0',
        libraries='lib1',
        is_pruned=True,
        ligo_only=True,
        current_history_id='h1',
        current_history_timestamp='2023-01-01T00:00:00',
        last_updated='2023-01-01T00:00:00'
    )
    job2 = GWFlowJob(
        id='job1',
        sname='S230101a',
        schema_version='1.0',
        libraries='lib1',
        is_pruned=True,
        ligo_only=True,
        current_history_id='h1',
        current_history_timestamp='2023-01-01T00:00:00',
        last_updated='2023-01-01T00:00:00'
    )
    job3 = GWFlowJob(
        id='job3',
        sname='S230101a',
        schema_version='1.0',
        libraries='lib1',
        is_pruned=True,
        ligo_only=True,
        current_history_id='h1',
        current_history_timestamp='2023-01-01T00:00:00',
        last_updated='2023-01-01T00:00:00'
    )
    assert job1 == job2
    assert job1 != job3


def test_gwflow_file_from_dict_zero_size():
    f = GWFlowFile.from_dict({
        'id': 'f1',
        'analysisUid': 'uid1',
        'path': '/p',
        'fileName': 'a.txt',
        'fileSize': 0,
        'uploaded': True,
        'downloadToken': 'tok1'
    })
    assert f.file_size == 0


def test_gwflow_event_id_from_dict_zero_gps_time():
    e = GWFlowEventID.from_dict({
        'eventId': 'evt1',
        'triggerId': 'trig1',
        'nickname': 'nick1',
        'gpsTime': 0.0
    })
    assert e.gps_time == 0.0


def test_gwflow_job_from_dict_defaults():
    job = GWFlowJob.from_dict({
        'id': 'job1',
        'sname': 'S230101a',
        'schema_version': '1.0',
        'libraries': 'lib1',
        'is_pruned': True,
        'ligo_only': True,
        'current_history_id': 'h1',
        'current_history_timestamp': '2023-01-01T00:00:00',
        'last_updated': '2023-01-01T00:00:00',
        'event_id': None
    })
    assert job.files == []
    assert job.bilby_jobs == []
    assert job.creation_time is None
    assert job.event_id is None
