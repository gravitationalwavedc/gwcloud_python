from gwcloud_python import GWCloud, FileReference, FileReferenceList, JobStatus, EventID
import pytest
from tempfile import TemporaryFile


@pytest.fixture
def mock_gwdc_init(mocker):
    def mock_init(self, token, endpoint):
        pass

    mocker.patch('gwdc_python.gwdc.GWDC.__init__', mock_init)


@pytest.fixture
def setup_mock_gwdc(mocker, mock_gwdc_init):
    def mock_gwdc(request_data):
        mock_request = mocker.Mock(return_value=request_data)
        mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)

    return mock_gwdc


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
            "is_uploaded_job": False
        }
    })

    return [job_file_data_1, job_file_data_2, job_file_data_3]


@pytest.fixture
def test_files():
    return FileReferenceList([
        FileReference(
            path='test/path_1.png',
            file_size=1,
            download_token='test_token_1',
            job_id='id1',
            uploaded=False
        ),
        FileReference(
            path='test/path_2.png',
            file_size=1,
            download_token='test_token_2',
            job_id='id1',
            uploaded=False
        ),
        FileReference(
            path='test/path_3.png',
            file_size=1,
            download_token='test_token_3',
            job_id='id1',
            uploaded=False
        ),
        FileReference(
            path='test/path_4.png',
            file_size=1,
            download_token='test_token_4',
            job_id='id2',
            uploaded=True
        ),
        FileReference(
            path='test/path_5.png',
            file_size=1,
            download_token='test_token_5',
            job_id='id2',
            uploaded=True
        ),
        FileReference(
            path='test/path_6.png',
            file_size=1,
            download_token='test_token_6',
            job_id='id2',
            uploaded=True
        ),
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

    assert job.job_id == single_job_request["id"]
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

    assert jobs[0].job_id == user_jobs[0]["id"]
    assert jobs[0].name == user_jobs[0]["name"]
    assert jobs[0].description == user_jobs[0]["description"]
    assert jobs[0].status == JobStatus(
        status=user_jobs[0]["job_status"]["name"],
        date=user_jobs[0]["job_status"]["date"]
    )
    assert jobs[0].event_id == EventID(**user_jobs[0]["event_id"])
    assert jobs[0].user == user_jobs[0]["user"]

    assert jobs[1].job_id == user_jobs[1]["id"]
    assert jobs[1].name == user_jobs[1]["name"]
    assert jobs[1].description == user_jobs[1]["description"]
    assert jobs[1].status == JobStatus(
        status=user_jobs[1]["job_status"]["name"],
        date=user_jobs[1]["job_status"]["date"]
    )
    assert jobs[1].event_id == EventID(**user_jobs[1]["event_id"])
    assert jobs[1].user == user_jobs[1]["user"]

    assert jobs[2].job_id == user_jobs[2]["id"]
    assert jobs[2].name == user_jobs[2]["name"]
    assert jobs[2].description == user_jobs[2]["description"]
    assert jobs[2].status == JobStatus(
        status=user_jobs[2]["job_status"]["name"],
        date=user_jobs[2]["job_status"]["date"]
    )
    assert jobs[2].event_id == EventID(**user_jobs[2]["event_id"])
    assert jobs[2].user == user_jobs[2]["user"]


def test_gwcloud_files_by_job_id(job_file_request):
    gwc = GWCloud(token='my_token')

    file_list, uploaded = gwc._get_files_by_job_id('arbitrary_job_id')

    for i, ref in enumerate(file_list):
        job_file_request[i].pop('is_dir', None)
        assert ref == FileReference(
            **job_file_request[i],
            job_id='arbitrary_job_id',
            uploaded=uploaded,
        )


def test_gwcloud_get_files_by_reference(setup_mock_download_fns, mocker, test_files):
    gwc = GWCloud(token='my_token')
    mock_download_files = setup_mock_download_fns[0]
    mock_get_fn = setup_mock_download_fns[1]
    mock_get_ids = setup_mock_download_fns[3]
    mock_ids = ['id10', 'id11', 'id12', 'id20', 'id21', 'id22']

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
        test_files.get_paths(),
        test_files.get_uploaded(),
        test_files.get_total_bytes()
    )


def test_gwcloud_save_batched_files(setup_mock_download_fns, mocker, test_files):
    gwc = GWCloud(token='my_token')
    mock_download_files = setup_mock_download_fns[0]
    mock_save_fn = setup_mock_download_fns[2]
    mock_get_ids = setup_mock_download_fns[3]
    mock_ids = ['id10', 'id11', 'id12', 'id20', 'id21', 'id22']

    gwc.save_files_by_reference(test_files, 'test_dir', preserve_directory_structure=True)

    mock_calls = [
        mocker.call(job_id, job_files.get_tokens())
        for job_id, job_files in test_files.batched.items()
    ]

    mock_get_ids.assert_has_calls(mock_calls)

    mock_download_files.assert_called_once_with(
        mock_save_fn,
        mock_ids,
        test_files.get_output_paths('test_dir', preserve_directory_structure=True),
        test_files.get_uploaded(),
        test_files.get_total_bytes()
    )
