from gwcloud_python import GWCloud, FileReference, FileReferenceList, JobStatus, EventID
from gwcloud_python.utils import convert_dict_keys
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
        "eventId": {
            "eventId": "GW123456"
        },
        "jobStatus": {
            "name": "Completed",
            "date": "2021-12-02"
        }
    }
    setup_mock_gwdc({"bilbyJob": job_data})
    return job_data


@pytest.fixture
def multi_job_request(setup_mock_gwdc):
    def modify_query_name(query_name):
        job_data_1 = {
            "id": 1,
            "name": "test_name_1",
            "description": "test description 1",
            "user": "Test User1",
            "eventId": {
                "eventId": "GW123456"
            },
            "jobStatus": {
                "name": "Completed",
                "date": "2021-01-01"
            }
        }

        job_data_2 = {
            "id": 2,
            "name": "test_name_2",
            "description": "test description 2",
            "user": "Test User2",
            "eventId": {
                "eventId": "GW123456"
            },
            "jobStatus": {
                "name": "Completed",
                "date": "2021-02-02"
            }
        }

        job_data_3 = {
            "id": 3,
            "name": "test_name_3",
            "description": "test description 3",
            "user": "Test User3",
            "eventId": {
                "eventId": "GW123456"
            },
            "jobStatus": {
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
        "fileSize": "1",
        "downloadToken": "test_token_1",
        "isDir": False
    }

    job_file_data_2 = {
        "path": "path/to/test.json",
        "fileSize": "10",
        "downloadToken": "test_token_2",
        "isDir": False
    }

    job_file_data_3 = {
        "path": "path/to/test",
        "fileSize": "100",
        "downloadToken": "test_token_3",
        "isDir": True
    }

    setup_mock_gwdc({
        "bilbyResultFiles": {
            "files": [
                job_file_data_1,
                job_file_data_2,
                job_file_data_3
            ],
            "isUploadedJob": False
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
            is_uploaded_job=False
        ),
        FileReference(
            path='test/path_2.png',
            file_size=1,
            download_token='test_token_2',
            job_id='id1',
            is_uploaded_job=False
        ),
        FileReference(
            path='test/path_3.png',
            file_size=1,
            download_token='test_token_3',
            job_id='id1',
            is_uploaded_job=False
        ),
        FileReference(
            path='test/path_4.png',
            file_size=1,
            download_token='test_token_4',
            job_id='id2',
            is_uploaded_job=True
        ),
        FileReference(
            path='test/path_5.png',
            file_size=1,
            download_token='test_token_5',
            job_id='id2',
            is_uploaded_job=True
        ),
        FileReference(
            path='test/path_6.png',
            file_size=1,
            download_token='test_token_6',
            job_id='id2',
            is_uploaded_job=True
        ),
    ])


@pytest.fixture
def setup_mock_download_fns(mocker, mock_gwdc_init, test_files):
    mock_files = mocker.Mock(return_value=[(f.path, TemporaryFile()) for f in test_files])

    return (
        mocker.patch('gwcloud_python.gwcloud._download_files', mock_files),
        mocker.patch('gwcloud_python.gwcloud._get_file_map_fn'),
        mocker.patch('gwcloud_python.gwcloud._save_file_map_fn'),
        mocker.patch('gwcloud_python.gwcloud.GWCloud._get_download_ids_from_tokens')
    )


@pytest.fixture
def user_jobs(multi_job_request):
    return multi_job_request('bilbyJobs')


def test_get_job_by_id(single_job_request):
    gwc = GWCloud(token='my_token')

    job = gwc.get_job_by_id('job_id')

    assert job.job_id == single_job_request["id"]
    assert job.name == single_job_request["name"]
    assert job.description == single_job_request["description"]
    assert job.status == JobStatus(
        status=single_job_request["jobStatus"]["name"],
        date=single_job_request["jobStatus"]["date"]
    )
    assert job.event_id == EventID(**convert_dict_keys(single_job_request["eventId"]))
    assert job.user == single_job_request["user"]


def test_get_user_jobs(user_jobs):
    gwc = GWCloud(token='my_token')

    jobs = gwc.get_user_jobs()

    assert jobs[0].job_id == user_jobs[0]["id"]
    assert jobs[0].name == user_jobs[0]["name"]
    assert jobs[0].description == user_jobs[0]["description"]
    assert jobs[0].status == JobStatus(
        status=user_jobs[0]["jobStatus"]["name"],
        date=user_jobs[0]["jobStatus"]["date"]
    )
    assert jobs[0].event_id == EventID(**convert_dict_keys(user_jobs[0]["eventId"]))
    assert jobs[0].user == user_jobs[0]["user"]

    assert jobs[1].job_id == user_jobs[1]["id"]
    assert jobs[1].name == user_jobs[1]["name"]
    assert jobs[1].description == user_jobs[1]["description"]
    assert jobs[1].status == JobStatus(
        status=user_jobs[1]["jobStatus"]["name"],
        date=user_jobs[1]["jobStatus"]["date"]
    )
    assert jobs[1].event_id == EventID(**convert_dict_keys(user_jobs[1]["eventId"]))
    assert jobs[1].user == user_jobs[1]["user"]

    assert jobs[2].job_id == user_jobs[2]["id"]
    assert jobs[2].name == user_jobs[2]["name"]
    assert jobs[2].description == user_jobs[2]["description"]
    assert jobs[2].status == JobStatus(
        status=user_jobs[2]["jobStatus"]["name"],
        date=user_jobs[2]["jobStatus"]["date"]
    )
    assert jobs[2].event_id == EventID(**convert_dict_keys(user_jobs[2]["eventId"]))
    assert jobs[2].user == user_jobs[2]["user"]


def test_gwcloud_files_by_job_id(job_file_request):
    gwc = GWCloud(token='my_token')

    file_list, is_uploaded_job = gwc._get_files_by_job_id('arbitrary_job_id')

    for i, ref in enumerate(file_list):
        job_file_request[i].pop('isDir')
        assert ref == FileReference(
            **convert_dict_keys(job_file_request[i]),
            job_id='arbitrary_job_id',
            is_uploaded_job=is_uploaded_job,
        )


def test_gwcloud_get_batched_files(setup_mock_download_fns, test_files):
    gwc = GWCloud(token='my_token')
    mock_download_files = setup_mock_download_fns[0]
    mock_get_fn = setup_mock_download_fns[1]
    mock_ids = setup_mock_download_fns[3].return_value

    test_files_subset = test_files[0:3]

    files = gwc._get_batched_files('id1', test_files_subset, is_uploaded_job=False)

    assert [f[0] for f in files] == test_files.get_paths()
    mock_download_files.assert_called_once_with(
        mock_get_fn,
        mock_ids,
        test_files_subset.get_paths(),
        test_files_subset.get_total_bytes(),
        False
    )


def test_gwcloud_save_batched_files(setup_mock_download_fns, test_files):
    gwc = GWCloud(token='my_token')
    mock_download_files = setup_mock_download_fns[0]
    mock_save_fn = setup_mock_download_fns[2]
    mock_ids = setup_mock_download_fns[3].return_value

    test_files_subset = test_files[0:3]

    gwc._save_batched_files(
        'id1',
        test_files_subset,
        'test_dir',
        preserve_directory_structure=True,
        is_uploaded_job=False
    )

    mock_download_files.assert_called_once_with(
        mock_save_fn,
        mock_ids,
        test_files_subset.get_output_paths('test_dir', preserve_directory_structure=True),
        test_files_subset.get_total_bytes(),
        False
    )


def test_gwcloud_get_files_by_reference(mock_gwdc_init, mocker, test_files):
    mock_fn = mocker.patch('gwcloud_python.gwcloud.GWCloud._get_batched_files')
    gwc = GWCloud(token='my_token')

    gwc.get_files_by_reference(test_files)

    batched_files = test_files._batch_by_job_id()
    mock_calls = [
        mocker.call(job_id=job_id, file_references=job_dict['files'], is_uploaded_job=job_dict['is_uploaded_job'])
        for job_id, job_dict in batched_files.items()
    ]

    mock_fn.assert_has_calls(mock_calls)


def test_gwcloud_save_files_by_reference(mock_gwdc_init, mocker, test_files):
    mock_fn = mocker.patch('gwcloud_python.gwcloud.GWCloud._save_batched_files')
    gwc = GWCloud(token='my_token')

    gwc.save_files_by_reference(test_files, root_path='test_dir', preserve_directory_structure=True)

    batched_files = test_files._batch_by_job_id()
    mock_calls = [
        mocker.call(
            job_id=job_id,
            file_references=job_dict['files'],
            root_path='test_dir',
            preserve_directory_structure=True,
            is_uploaded_job=job_dict['is_uploaded_job']
        )
        for job_id, job_dict in batched_files.items()
    ]

    mock_fn.assert_has_calls(mock_calls)
