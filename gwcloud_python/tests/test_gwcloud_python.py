import os
import pytest
from tempfile import NamedTemporaryFile, TemporaryFile

from gwdc_python.files.constants import GWDCObjectType
from gwdc_python.files import FileReference, FileReferenceList
from gwdc_python.helpers import JobStatus

from gwcloud_python import GWCloud, BilbyJob, EventID


@pytest.fixture
def mock_gwdc_init(mocker):
    def mock_init(self, token, endpoint, custom_error_handler=None):
        pass

    mocker.patch('gwdc_python.gwdc.GWDC.__init__', mock_init)


@pytest.fixture
def setup_mock_gwdc(mocker, mock_gwdc_init):
    def mock_gwdc(request_data):
        mock_request = mocker.Mock(return_value=request_data)
        mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)

    return mock_gwdc


@pytest.fixture
def mock_bilby_job():
    def _mock_bilby_job(client, i=1, _type=GWDCObjectType.NORMAL):
        job = BilbyJob(
            client=client,
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
def single_job_request(setup_mock_gwdc):
    job_data = {
        "id": 1,
        "name": "test_name",
        "description": "test description",
        "user": "Test User1",
        "event_id": {
            "event_id": "GW123456"
        },
        "job_status": {
            "name": "Completed",
            "date": "2021-12-02"
        }
    }
    setup_mock_gwdc({"bilby_job": job_data})
    return job_data


@pytest.fixture
def multi_job_request(setup_mock_gwdc):
    def modify_query_name(query_name):
        job_data_1 = {
            "id": 1,
            "name": "test_name_1",
            "description": "test description 1",
            "user": "Test User1",
            "event_id": {
                "event_id": "GW123456"
            },
            "job_status": {
                "name": "Completed",
                "date": "2021-01-01"
            }
        }

        job_data_2 = {
            "id": 2,
            "name": "test_name_2",
            "description": "test description 2",
            "user": "Test User2",
            "event_id": {
                "event_id": "GW123456"
            },
            "job_status": {
                "name": "Completed",
                "date": "2021-02-02"
            }
        }

        job_data_3 = {
            "id": 3,
            "name": "test_name_3",
            "description": "test description 3",
            "user": "Test User3",
            "event_id": {
                "event_id": "GW123456"
            },
            "job_status": {
                "name": "Error",
                "date": "2021-03-03"
            }
        }

        setup_mock_gwdc({
            query_name: {
                "edges": [
                    {"node": job_data_1},
                    {"node": job_data_2},
                    {"node": job_data_3},
                ]
            }
        })

        return [job_data_1, job_data_2, job_data_3]

    return modify_query_name


@pytest.fixture
def job_file_request(setup_mock_gwdc):
    job_file_data_1 = {
        "path": "path/to/test.png",
        "file_size": "1",
        "download_token": "test_token_1",
        "is_dir": False
    }

    job_file_data_2 = {
        "path": "path/to/test.json",
        "file_size": "10",
        "download_token": "test_token_2",
        "is_dir": False
    }

    job_file_data_3 = {
        "path": "path/to/test",
        "file_size": "100",
        "download_token": "test_token_3",
        "is_dir": True
    }

    setup_mock_gwdc({
        "bilby_result_files": {
            "files": [
                job_file_data_1,
                job_file_data_2,
                job_file_data_3
            ],
            "job_type": GWDCObjectType.NORMAL
        }
    })

    return [job_file_data_1, job_file_data_2, job_file_data_3]


@pytest.fixture
def test_files(mocker, mock_bilby_job):
    job1 = mock_bilby_job(mocker.Mock(), 1, GWDCObjectType.NORMAL)
    job2 = mock_bilby_job(mocker.Mock(), 2, GWDCObjectType.UPLOADED)
    job3 = mock_bilby_job(mocker.Mock(), 3, GWDCObjectType.EXTERNAL)
    return FileReferenceList([
        FileReference(
            path='test/path_1.png',
            file_size=1,
            download_token='test_token_1',
            parent=job1
        ),
        FileReference(
            path='test/path_2.png',
            file_size=1,
            download_token='test_token_2',
            parent=job1
        ),
        FileReference(
            path='test/path_3.png',
            file_size=1,
            download_token='test_token_3',
            parent=job1
        ),
        FileReference(
            path='test/path_4.png',
            file_size=1,
            download_token='test_token_4',
            parent=job2
        ),
        FileReference(
            path='test/path_5.png',
            file_size=1,
            download_token='test_token_5',
            parent=job2
        ),
        FileReference(
            path='test/path_6.png',
            file_size=1,
            download_token='test_token_6',
            parent=job2
        ),
        FileReference(
            path='https://anotherurl.net/test/whatever/',
            file_size=None,
            download_token=None,
            parent=job3
        )
    ])


@pytest.fixture
def setup_mock_download_fns(mocker, mock_gwdc_init, test_files):
    mock_files = mocker.Mock(return_value=[(f.path, TemporaryFile()) for f in test_files])

    def get_mock_ids(job_id, tokens):
        return [f'{job_id}{i}' for i, _ in enumerate(tokens)]

    mock_ids = mocker.Mock(side_effect=get_mock_ids)
    return (
        mocker.patch('gwcloud_python.gwcloud._download_files', mock_files),
        mocker.patch('gwcloud_python.gwcloud._get_file_map_fn'),
        mocker.patch('gwcloud_python.gwcloud._save_file_map_fn'),
        mocker.patch('gwcloud_python.gwcloud.GWCloud._get_download_ids_from_tokens', mock_ids)
    )


@pytest.fixture
def user_jobs(multi_job_request):
    return multi_job_request('bilby_jobs')


def test_get_job_by_id(single_job_request):
    gwc = GWCloud(token='my_token')

    job = gwc.get_job_by_id('job_id')

    assert job.id == single_job_request["id"]
    assert job.name == single_job_request["name"]
    assert job.description == single_job_request["description"]
    assert job.status == JobStatus(
        status=single_job_request["job_status"]["name"],
        date=single_job_request["job_status"]["date"]
    )
    assert job.event_id == EventID(**single_job_request["event_id"])
    assert job.user == single_job_request["user"]


def test_get_user_jobs(user_jobs):
    gwc = GWCloud(token='my_token')

    jobs = gwc.get_user_jobs()

    assert jobs[0].id == user_jobs[0]["id"]
    assert jobs[0].name == user_jobs[0]["name"]
    assert jobs[0].description == user_jobs[0]["description"]
    assert jobs[0].status == JobStatus(
        status=user_jobs[0]["job_status"]["name"],
        date=user_jobs[0]["job_status"]["date"]
    )
    assert jobs[0].event_id == EventID(**user_jobs[0]["event_id"])
    assert jobs[0].user == user_jobs[0]["user"]

    assert jobs[1].id == user_jobs[1]["id"]
    assert jobs[1].name == user_jobs[1]["name"]
    assert jobs[1].description == user_jobs[1]["description"]
    assert jobs[1].status == JobStatus(
        status=user_jobs[1]["job_status"]["name"],
        date=user_jobs[1]["job_status"]["date"]
    )
    assert jobs[1].event_id == EventID(**user_jobs[1]["event_id"])
    assert jobs[1].user == user_jobs[1]["user"]

    assert jobs[2].id == user_jobs[2]["id"]
    assert jobs[2].name == user_jobs[2]["name"]
    assert jobs[2].description == user_jobs[2]["description"]
    assert jobs[2].status == JobStatus(
        status=user_jobs[2]["job_status"]["name"],
        date=user_jobs[2]["job_status"]["date"]
    )
    assert jobs[2].event_id == EventID(**user_jobs[2]["event_id"])
    assert jobs[2].user == user_jobs[2]["user"]


def test_gwcloud_files_by_bilby_job(job_file_request, mock_bilby_job):
    gwc = GWCloud(token='my_token')

    job = mock_bilby_job(gwc)
    file_list = gwc._get_files_by_bilby_job(job)

    for i, ref in enumerate(file_list):
        job_file_request[i].pop('is_dir', None)
        assert ref == FileReference(
            **job_file_request[i],
            parent=job
        )


def test_gwcloud_get_files_by_reference(setup_mock_download_fns, mocker, test_files):
    gwc = GWCloud(token='my_token')
    mock_download_files = setup_mock_download_fns[0]
    mock_get_fn = setup_mock_download_fns[1]
    mock_get_ids = setup_mock_download_fns[3]
    mock_ids = ['id10', 'id11', 'id12', 'id20', 'id21', 'id22', 'id30']

    files = gwc.get_files_by_reference(test_files)

    mock_calls = [
        mocker.call(job_id, job_files.get_tokens())
        for job_id, job_files in test_files.batched.items()
    ]

    mock_get_ids.assert_has_calls(mock_calls)

    assert [f[0] for f in files] == test_files.get_paths()
    mock_download_files.assert_called_once_with(
        mock_get_fn,
        mock_ids,
        test_files
    )


def test_gwcloud_save_batched_files(setup_mock_download_fns, mocker, test_files):
    gwc = GWCloud(token='my_token')
    mock_download_files = setup_mock_download_fns[0]
    mock_save_fn = setup_mock_download_fns[2]
    mock_get_ids = setup_mock_download_fns[3]
    mock_ids = ['id10', 'id11', 'id12', 'id20', 'id21', 'id22', 'id30']

    mock_root_path = 'test_dir'

    gwc.save_files_by_reference(test_files, mock_root_path)

    mock_calls = [
        mocker.call(job_id, job_files.get_tokens())
        for job_id, job_files in test_files.batched.items()
    ]

    mock_get_ids.assert_has_calls(mock_calls)

    mock_download_files.assert_called_once_with(
        mock_save_fn,
        mock_ids,
        test_files,
        mock_root_path
    )


def test_upload_hdf5_job(setup_mock_gwdc, mock_bilby_job, mocker):
    """Test uploading a job with HDF5 file and INI file."""
    
    # Mock the upload token generation
    mocker.patch('gwcloud_python.gwcloud.GWCloud._generate_upload_token', return_value='test_upload_token')
    
    # Mock the response from the upload mutation
    upload_response = {
        'upload_hdf5_bilby_job': {
            'result': {
                'job_id': 'test_job_id'
            }
        }
    }
    
    # Mock the job retrieval
    job_data = {
        'bilby_job': {
            'id': 'test_job_id',
            'name': 'Test HDF5 Job',
            'description': 'Test Description',
            'user': 'Test User',
            'event_id': None,
            'job_status': {
                'name': 'Completed',
                'date': '2021-12-02'
            },
        }
    }
    
    # Mock the request method to return different responses for different calls
    mock_request = mocker.Mock(side_effect=[upload_response, job_data])
    mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)
    
    # Create temporary files
    with NamedTemporaryFile(suffix='.hdf5', delete=False) as hdf5_file:
        hdf5_file.write(b'fake_hdf5_content')
        hdf5_path = hdf5_file.name
    
    with NamedTemporaryFile(suffix='.ini', delete=False) as ini_file:
        ini_file.write(b'label=test_job\noutdir=./')
        ini_path = ini_file.name
    
    try:
        gwc = GWCloud()
        job = gwc.upload_hdf5_job(
            description="Test HDF5 Job",
            hdf5_file=hdf5_path,
            ini_file=ini_path,
            public=True
        )
        
        assert isinstance(job, BilbyJob)
        assert job.id == 'test_job_id'
        assert job.name == 'Test HDF5 Job'
        assert job.description == 'Test Description'
        
    finally:
        # Clean up temporary files
        os.unlink(hdf5_path)
        os.unlink(ini_path)


def test_upload_hdf5_job_private(setup_mock_gwdc, mock_bilby_job, mocker):
    """Test uploading a private HDF5 job."""
    
    # Mock the upload token generation
    mocker.patch('gwcloud_python.gwcloud.GWCloud._generate_upload_token', return_value='test_upload_token')
    
    # Mock the response from the upload mutation
    upload_response = {
        'upload_hdf5_bilby_job': {
            'result': {
                'job_id': 'test_job_id'
            }
        }
    }
    
    # Mock the job retrieval
    job_data = {
        'bilby_job': {
            'id': 'test_job_id',
            'name': 'Test Private HDF5 Job',
            'description': 'Test Private Description',
            'user': 'Test User',
            'event_id': None,
            'job_status': {
                'name': 'Completed',
                'date': '2021-12-02'
            },
        }
    }
    
    # Mock the request method to return different responses for different calls
    mock_request = mocker.Mock(side_effect=[upload_response, job_data])
    mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)
    
    # Create temporary files
    with NamedTemporaryFile(suffix='.hdf5', delete=False) as hdf5_file:
        hdf5_file.write(b'fake_hdf5_content')
        hdf5_path = hdf5_file.name
    
    with NamedTemporaryFile(suffix='.ini', delete=False) as ini_file:
        ini_file.write(b'label=test_private_job\noutdir=./')
        ini_path = ini_file.name
    
    try:
        gwc = GWCloud()
        job = gwc.upload_hdf5_job(
            description="Test Private HDF5 Job",
            hdf5_file=hdf5_path,
            ini_file=ini_path,
            public=False  # Private job
        )
        
        assert isinstance(job, BilbyJob)
        assert job.id == 'test_job_id'
        assert job.name == 'Test Private HDF5 Job'
        assert job.description == 'Test Private Description'
        
    finally:
        # Clean up temporary files
        os.unlink(hdf5_path)
        os.unlink(ini_path)


def _removed_event_name():
    return "is_" + "ligo_" + "event"


def _removed_event_graphql_name():
    return "is" + "Ligo" + "Event"


def _event_payload():
    return {
        "event_id": "GW123456_123456",
        "trigger_id": "S123456a",
        "nickname": "test",
        "gps_time": 1126259462.391,
    }


def _bilby_payload():
    return {
        "id": "job-id",
        "name": "job",
        "description": "description",
        "user": "user",
        "event_id": _event_payload(),
        "job_status": {"name": "Completed", "date": "2021-01-01"},
    }


def test_event_id_field_free_model_shape():
    event = EventID(**_event_payload())

    assert event.event_id == "GW123456_123456"
    assert not hasattr(event, _removed_event_name())


@pytest.mark.parametrize(
    ("method_name", "arguments", "response"),
    [
        (
            "get_public_job_list",
            (),
            {"public_bilby_jobs": {"edges": [{"node": _bilby_payload()}]}},
        ),
        (
            "get_job_by_id",
            ("job-id",),
            {"bilby_job": _bilby_payload()},
        ),
        (
            "get_user_jobs",
            (),
            {"bilby_jobs": {"edges": [{"node": _bilby_payload()}]}},
        ),
    ],
)
def test_bilby_queries_exclude_removed_event_field(
    mock_gwdc_init, mocker, method_name, arguments, response
):
    mock_request = mocker.Mock(return_value=response)
    mocker.patch("gwdc_python.gwdc.GWDC.request", mock_request)
    gwc = GWCloud(token="my_token")

    getattr(gwc, method_name)(*arguments)

    assert _removed_event_graphql_name() not in mock_request.call_args.kwargs["query"]


def test_create_event_id_request_shape(mock_gwdc_init, mocker):
    payload = _event_payload()
    mock_request = mocker.Mock(
        side_effect=[
            {"create_event_id": {"result": "created"}},
            {"event_id": payload},
        ]
    )
    mocker.patch("gwdc_python.gwdc.GWDC.request", mock_request)
    gwc = GWCloud(token="my_token")

    event = gwc.create_event_id(
        payload["event_id"],
        payload["gps_time"],
        trigger_id=payload["trigger_id"],
        nickname=payload["nickname"],
    )

    mutation_call, detail_call = mock_request.call_args_list
    assert _removed_event_graphql_name() not in mutation_call.kwargs["variables"]["input"]
    assert _removed_event_graphql_name() not in detail_call.kwargs["query"]
    assert event == EventID(**payload)


def test_update_event_id_preserves_optional_gps_null(mock_gwdc_init, mocker):
    payload = _event_payload()
    mock_request = mocker.Mock(
        side_effect=[
            {"update_event_id": {"result": "updated"}},
            {"event_id": payload},
        ]
    )
    mocker.patch("gwdc_python.gwdc.GWDC.request", mock_request)
    gwc = GWCloud(token="my_token")

    gwc.update_event_id(payload["event_id"], nickname="updated")

    mutation_call, detail_call = mock_request.call_args_list
    variables = mutation_call.kwargs["variables"]["input"]
    assert variables["gpsTime"] is None
    assert _removed_event_graphql_name() not in variables
    assert _removed_event_graphql_name() not in detail_call.kwargs["query"]


def test_all_event_ids_query_excludes_removed_field(mock_gwdc_init, mocker):
    payload = _event_payload()
    mock_request = mocker.Mock(return_value={"all_event_ids": [payload]})
    mocker.patch("gwdc_python.gwdc.GWDC.request", mock_request)
    gwc = GWCloud(token="my_token")

    events = gwc.get_all_event_ids()

    assert events == [EventID(**payload)]
    assert _removed_event_graphql_name() not in mock_request.call_args.kwargs["query"]


@pytest.mark.parametrize("method_name", ["create_event_id", "update_event_id"])
def test_removed_event_keyword_raises_type_error(mock_gwdc_init, method_name):
    gwc = GWCloud(token="my_token")
    kwargs = {_removed_event_name(): True}

    with pytest.raises(TypeError):
        getattr(gwc, method_name)("GW123456_123456", **kwargs)
