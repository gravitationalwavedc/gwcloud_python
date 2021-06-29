import pytest
from pathlib import Path
from gwcloud_python.utils import file_lists


@pytest.fixture
def png_data():
    return [
        {'path': Path('data/dir/test1.png')},
        {'path': Path('data/dir/test2.png')},
    ]


@pytest.fixture
def png_result():
    return [
        {'path': Path('result/dir/test1.png')},
        {'path': Path('result/dir/test2.png')},
    ]


@pytest.fixture
def png_extra():
    return [
        {'path': Path('test1.png')},
        {'path': Path('test2.png')},
        {'path': Path('arbitrary/dir/test1.png')},
        {'path': Path('arbitrary/dir/test2.png')},
    ]


@pytest.fixture
def corner():
    return [
        {'path': Path('test1_corner.png')},
        {'path': Path('test2_corner.png')},
    ]


@pytest.fixture
def index():
    return [
        {'path': Path('index.html')},
    ]


@pytest.fixture
def config():
    return [
        {'path': Path('a_config_complete.ini')},
    ]


@pytest.fixture
def merge():
    return [
        {'path': Path('result/dir/a_merge_result.json')},
    ]


@pytest.fixture
def unmerge():
    return [
        {'path': Path('result/dir/a_result.json')},
    ]


@pytest.fixture
def png(png_data, png_result, png_extra, corner):
    return png_data + png_result + png_extra + corner


@pytest.fixture
def default_with_merge(png_data, png_result, index, config, merge):
    return png_data + png_result + index + config + merge


@pytest.fixture
def full_with_merge(png, index, config, merge, unmerge):
    return png + index + config + merge + unmerge


@pytest.fixture
def default_without_merge(png_data, png_result, index, config, unmerge):
    return png_data + png_result + index + config + unmerge


@pytest.fixture
def full_without_merge(png, index, config, unmerge):
    return png + index + config + unmerge


def test_default_file_list(full_with_merge, default_with_merge, full_without_merge, default_without_merge):
    sub_list = file_lists.default_filter(full_with_merge)
    assert file_lists.sort_file_list(sub_list) == file_lists.sort_file_list(default_with_merge)

    sub_list = file_lists.default_filter(full_without_merge)
    assert file_lists.sort_file_list(sub_list) == file_lists.sort_file_list(default_without_merge)


def test_png_file_list(full_with_merge, png):
    sub_list = file_lists.png_filter(full_with_merge)
    assert file_lists.sort_file_list(sub_list) == file_lists.sort_file_list(png)


def test_config_file_list(full_with_merge, config):
    sub_list = file_lists.config_filter(full_with_merge)
    assert file_lists.sort_file_list(sub_list) == file_lists.sort_file_list(config)


def test_corner_file_list(full_with_merge, corner):
    sub_list = file_lists.corner_plot_filter(full_with_merge)
    assert file_lists.sort_file_list(sub_list) == file_lists.sort_file_list(corner)
