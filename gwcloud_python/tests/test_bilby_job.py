import pytest
from gwdc_python.files.constants import GWDCObjectType

from gwcloud_python import BilbyJob, FileReference, FileReferenceList, EventID
from gwcloud_python.utils import file_filters


@pytest.fixture
def placeholder_bilby_job(mocker):
    return mocker.Mock(**{'is_external.return_value': False})


@pytest.fixture
def png_data_result(placeholder_bilby_job):
    return FileReferenceList([
        FileReference(
            path='data/dir/test1.png',
            file_size='1',
            download_token='test_token_1',
            parent=placeholder_bilby_job
        ),
        FileReference(
            path='data/dir/test2.png',
            file_size='1',
            download_token='test_token_2',
            parent=placeholder_bilby_job
        ),
        FileReference(
            path='result/dir/test1.png',
            file_size='1',
            download_token='test_token_3',
            parent=placeholder_bilby_job
        ),
        FileReference(
            path='result/dir/test2.png',
            file_size='1',
            download_token='test_token_4',
            parent=placeholder_bilby_job
        ),
    ])


@pytest.fixture
def png_extra(placeholder_bilby_job):
    return FileReferenceList([
        FileReference(
            path='test1.png',
            file_size='1',
            download_token='test_token_5',
            parent=placeholder_bilby_job
        ),
        FileReference(
            path='test2.png',
            file_size='1',
            download_token='test_token_6',
            parent=placeholder_bilby_job
        ),
        FileReference(
            path='arbitrary/dir/test1.png',
            file_size='1',
            download_token='test_token_7',
            parent=placeholder_bilby_job
        ),
        FileReference(
            path='arbitrary/dir/test2.png',
            file_size='1',
            download_token='test_token_8',
            parent=placeholder_bilby_job
        ),
    ])


@pytest.fixture
def corner(placeholder_bilby_job):
    return FileReferenceList([
        FileReference(
            path='test1_corner.png',
            file_size='1',
            download_token='test_token_9',
            parent=placeholder_bilby_job
        ),
        FileReference(
            path='test2_corner.png',
            file_size='1',
            download_token='test_token_10',
            parent=placeholder_bilby_job
        ),
    ])


@pytest.fixture
def config(placeholder_bilby_job):
    return FileReferenceList([
        FileReference(
            path='a_config_complete.ini',
            file_size='1',
            download_token='test_token_11',
            parent=placeholder_bilby_job
        ),
    ])


@pytest.fixture
def json(placeholder_bilby_job):
    return FileReferenceList([
        FileReference(
            path='result/dir/a_merge_result.json',
            file_size='1',
            download_token='test_token_12',
            parent=placeholder_bilby_job
        ),
    ])


@pytest.fixture
def index(placeholder_bilby_job):
    return FileReferenceList([
        FileReference(
            path='index.html',
            file_size='1',
            download_token='test_token_13',
            parent=placeholder_bilby_job
        ),
    ])


@pytest.fixture
def png(png_data_result, png_extra, corner):
    return png_data_result + png_extra + corner


@pytest.fixture
def default(png_data_result, config, json, index):
    return png_data_result + config + json + index


@pytest.fixture
def full(png, config, json, index):
    return png + config + json + index


@pytest.fixture
def mock_bilby_job(mocker):
    def bilby_job(methods):
        config_dict = {f'{key}.return_value': value for key, value in methods.items()}
        return BilbyJob(
            client=mocker.Mock(**config_dict),
            job_id='test_id',
            name='TestName',
            description='Test description',
            user='Test User',
            event_id={'event_id': 'GW123456'},
            job_status={
                'name': 'Completed',
                'date': '2021-12-02'
            },
        )

    return bilby_job


@pytest.fixture
def mock_bilby_job_files(mock_bilby_job, full):
    job = mock_bilby_job({'_get_files_by_bilby_job': full})
    job.type = GWDCObjectType.NORMAL
    return job


@pytest.fixture
def mock_bilby_job_update(mock_bilby_job):
    return mock_bilby_job({'request': {'update_bilby_job': {'result': 'Success'}}})


@pytest.fixture
def update_query():
    return """
            mutation BilbyJobEventIDMutation($input: UpdateBilbyJobMutationInput!) {
                updateBilbyJob(input: $input) {
                    result
                }
            }
        """


def test_bilby_job_full_file_list(mock_bilby_job_files, full):
    bilby_job = mock_bilby_job_files
    assert bilby_job.get_full_file_list() == full

    bilby_job.client._get_files_by_bilby_job.assert_called_once()


def test_bilby_job_file_filters(mocker, mock_bilby_job_files, full, default, png, corner, config):
    bilby_job = mock_bilby_job_files

    assert file_filters.sort_file_list(bilby_job.get_default_file_list()) == file_filters.sort_file_list(default)
    assert file_filters.sort_file_list(bilby_job.get_png_file_list()) == file_filters.sort_file_list(png)
    assert file_filters.sort_file_list(bilby_job.get_corner_plot_file_list()) == file_filters.sort_file_list(corner)
    assert file_filters.sort_file_list(bilby_job.get_config_file_list()) == file_filters.sort_file_list(config)

    assert bilby_job.client._get_files_by_bilby_job.call_count == 4


def test_bilbyjob_set_name(mock_bilby_job_update, update_query):
    bilby_job = mock_bilby_job_update

    assert bilby_job.name == 'TestName'
    bilby_job.set_name(name='ADifferentName')
    assert bilby_job.name == 'ADifferentName'
    bilby_job.client.request.assert_called_once_with(
        query=update_query,
        variables={
            'input': {
                'job_id': bilby_job.id,
                'name': 'ADifferentName'
            }
        }
    )


def test_bilbyjob_set_description(mock_bilby_job_update, update_query):
    bilby_job = mock_bilby_job_update

    assert bilby_job.description == 'Test description'
    bilby_job.set_description(description='A different description')
    assert bilby_job.description == 'A different description'
    bilby_job.client.request.assert_called_once_with(
        query=update_query,
        variables={
            'input': {
                'job_id': bilby_job.id,
                'description': 'A different description'
            }
        }
    )


def test_bilbyjob_set_event_id(mock_bilby_job, update_query):
    bilby_job = mock_bilby_job({
        'request': {'update_bilby_job': {'result': 'Success'}},
        'get_event_id': EventID(event_id='GW111111')
    })

    assert bilby_job.event_id == EventID(event_id='GW123456')
    bilby_job.set_event_id(event_id='GW111111')
    assert bilby_job.event_id == EventID(event_id='GW111111')
    bilby_job.client.request.assert_called_once_with(
        query=update_query,
        variables={
            'input': {
                'job_id': bilby_job.id,
                'event_id': 'GW111111'
            }
        }
    )
