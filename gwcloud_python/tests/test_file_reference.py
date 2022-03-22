from gwcloud_python import FileReference, FileReferenceList
import pytest
from pathlib import Path
from gwcloud_python.utils import remove_path_anchor


@pytest.fixture
def setup_dicts():
    return [
        {
            'path': 'data/dir/test1.png',
            'file_size': '1',
            'download_token': 'test_token_1',
            'job_id': 'id1',
            'is_uploaded_job': False
        },
        {
            'path': 'data/dir/test2.png',
            'file_size': '1',
            'download_token': 'test_token_2',
            'job_id': 'id1',
            'is_uploaded_job': False
        },
        {
            'path': 'result/dir/test1.txt',
            'file_size': '1',
            'download_token': 'test_token_3',
            'job_id': 'id2',
            'is_uploaded_job': True
        },
        {
            'path': 'result/dir/test2.txt',
            'file_size': '1',
            'download_token': 'test_token_4',
            'job_id': 'id2',
            'is_uploaded_job': True
        },
        {
            'path': 'test1.json',
            'file_size': '1',
            'download_token': 'test_token_5',
            'job_id': 'id3',
            'is_uploaded_job': False
        },
        {
            'path': 'test2.json',
            'file_size': '1',
            'download_token': 'test_token_6',
            'job_id': 'id3',
            'is_uploaded_job': False
        },
    ]


def test_file_reference(setup_dicts):
    for file_dict in setup_dicts:
        ref = FileReference(**file_dict)
        assert ref.path == remove_path_anchor(Path(file_dict['path']))
        assert ref.file_size == int(file_dict['file_size'])
        assert ref.download_token == file_dict['download_token']
        assert ref.job_id == file_dict['job_id']
        assert ref.is_uploaded_job == file_dict['is_uploaded_job']


def test_file_reference_list(setup_dicts):
    file_references = [FileReference(**file_dict) for file_dict in setup_dicts]
    file_reference_list = FileReferenceList(file_references)

    for i, ref in enumerate(file_reference_list):
        assert ref.path == file_references[i].path
        assert ref.file_size == file_references[i].file_size
        assert ref.download_token == file_references[i].download_token
        assert ref.job_id == file_references[i].job_id
        assert ref.is_uploaded_job == file_references[i].is_uploaded_job

    assert file_reference_list.get_total_bytes() == sum([ref.file_size for ref in file_references])
    assert file_reference_list.get_tokens() == [ref.download_token for ref in file_references]
    assert file_reference_list.get_paths() == [ref.path for ref in file_references]


def test_file_reference_list_output_paths(setup_dicts):
    file_reference_list = FileReferenceList([FileReference(**file_dict) for file_dict in setup_dicts])

    root_path = Path('test_dir')
    output_paths = [
        root_path / 'data/dir/test1.png',
        root_path / 'data/dir/test2.png',
        root_path / 'result/dir/test1.txt',
        root_path / 'result/dir/test2.txt',
        root_path / 'test1.json',
        root_path / 'test2.json'
    ]
    output_paths_flat = [
        root_path / 'test1.png',
        root_path / 'test2.png',
        root_path / 'test1.txt',
        root_path / 'test2.txt',
        root_path / 'test1.json',
        root_path / 'test2.json'
    ]
    assert output_paths == file_reference_list.get_output_paths(root_path)
    assert output_paths_flat == file_reference_list.get_output_paths(root_path, preserve_directory_structure=False)


def test_batch_file_reference_list(setup_dicts):
    file_reference_list = FileReferenceList([FileReference(**file_dict) for file_dict in setup_dicts])

    batched = {
        'id1': {
            'files': file_reference_list[0:2],
            'is_uploaded_job': False
        },
        'id2': {
            'files': file_reference_list[2:4],
            'is_uploaded_job': True
        },
        'id3': {
            'files': file_reference_list[4:6],
            'is_uploaded_job': False
        },
    }

    assert file_reference_list._batch_by_job_id() == batched
