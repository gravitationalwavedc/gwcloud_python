from gwcloud_python import GWCloud
import pytest


@pytest.fixture
def setup_mock_gwdc(mocker):
    def mock_gwdc(request_data):
        def mock_init(self, token, endpoint):
            pass

        def mock_request(self, query, variables=None, headers=None):
            data = request_data
            errors = None
            return data, errors

        mocker.patch('gwdc_python.gwdc.GWDC.__init__', mock_init)
        mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)

    return mock_gwdc


@pytest.fixture
def single_job_request(setup_mock_gwdc):
    job_data = {
        "id": 1,
        "name": "test_name",
        "description": "test description",
        "userId": 1
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
            "userId": 1
        }

        job_data_2 = {
            "id": 2,
            "name": "test_name_2",
            "description": "test description 2",
            "userId": 2
        }

        job_data_3 = {
            "id": 3,
            "name": "test_name_3",
            "description": "test description 3",
            "userId": 3
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
def user_jobs(multi_job_request):
    return multi_job_request('bilbyJobs')


def test_get_job_by_id(single_job_request):
    gwc = GWCloud(token='my_token')

    job = gwc._get_job_by_id('job_id')

    assert job.job_id == single_job_request["id"]
    assert job.name == single_job_request["name"]
    assert job.description == single_job_request["description"]
    assert job.other['userId'] == single_job_request["userId"]


def test_get_user_jobs(user_jobs):
    gwc = GWCloud(token='my_token')

    jobs = gwc._get_user_jobs()

    assert jobs[0].job_id == user_jobs[0]["id"]
    assert jobs[0].name == user_jobs[0]["name"]
    assert jobs[0].description == user_jobs[0]["description"]
    assert jobs[0].other['userId'] == user_jobs[0]["userId"]

    assert jobs[1].job_id == user_jobs[1]["id"]
    assert jobs[1].name == user_jobs[1]["name"]
    assert jobs[1].description == user_jobs[1]["description"]
    assert jobs[1].other['userId'] == user_jobs[1]["userId"]

    assert jobs[2].job_id == user_jobs[2]["id"]
    assert jobs[2].name == user_jobs[2]["name"]
    assert jobs[2].description == user_jobs[2]["description"]
    assert jobs[2].other['userId'] == user_jobs[2]["userId"]
