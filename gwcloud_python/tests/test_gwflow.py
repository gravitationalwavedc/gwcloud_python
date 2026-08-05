import os
import json
import pytest
from datetime import datetime
from tempfile import NamedTemporaryFile

from gwcloud_python import GWCloud
from gwcloud_python.gwflow import GWFlowPendingFile, GWFlowJobUpsertResult

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
