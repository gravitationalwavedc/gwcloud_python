from pathlib import Path
from gwcloud_python.utils import identifiers


def test_file_suffix_funcs():
    png_test_path = Path('/this/is/a/test.png')
    html_test_path = Path('/this/is/a/test.html')
    no_suffix_test_path = Path('/this/is/a/test')

    assert identifiers.png_file(png_test_path) is True
    assert identifiers.png_file(html_test_path) is False
    assert identifiers.png_file(no_suffix_test_path) is False

    assert identifiers.html_file(png_test_path) is False
    assert identifiers.html_file(html_test_path) is True
    assert identifiers.png_file(no_suffix_test_path) is False


def test_file_beginning_funcs():
    data_dir_test_path = Path('/data/this/is/a/test')
    relative_data_dir_test_path = Path('data/this/is/a/test')
    result_dir_test_path = Path('/result/this/is/a/test')
    relative_result_dir_test_path = Path('result/this/is/a/test')
    no_dir_test_path1 = Path('data.png')
    no_dir_test_path2 = Path('/data.png')

    assert identifiers.data_dir(data_dir_test_path) is False
    assert identifiers.data_dir(relative_data_dir_test_path) is True
    assert identifiers.data_dir(result_dir_test_path) is False
    assert identifiers.data_dir(relative_result_dir_test_path) is False
    assert identifiers.result_dir(data_dir_test_path) is False
    assert identifiers.result_dir(relative_data_dir_test_path) is False
    assert identifiers.result_dir(result_dir_test_path) is False
    assert identifiers.result_dir(relative_result_dir_test_path) is True
    assert identifiers.data_dir(no_dir_test_path1) is False
    assert identifiers.data_dir(no_dir_test_path2) is False


def test_file_ending_funcs():
    config_complete_test_path = Path('/this/is/a_config_complete.ini')
    merged_json_test_path = Path('/this/is/a_merge_result.json')
    corner_plot_test_path = Path('/this/is/a_corner.png')
    no_suffix_test_path = Path('/this/is/a/test')

    assert identifiers.config_file(config_complete_test_path) is True
    assert identifiers.config_file(merged_json_test_path) is False
    assert identifiers.config_file(corner_plot_test_path) is False
    assert identifiers.config_file(no_suffix_test_path) is False

    assert identifiers.merged_json_file(config_complete_test_path) is False
    assert identifiers.merged_json_file(merged_json_test_path) is True
    assert identifiers.merged_json_file(corner_plot_test_path) is False
    assert identifiers.merged_json_file(no_suffix_test_path) is False

    assert identifiers.corner_plot_file(config_complete_test_path) is False
    assert identifiers.corner_plot_file(merged_json_test_path) is False
    assert identifiers.corner_plot_file(corner_plot_test_path) is True
    assert identifiers.corner_plot_file(no_suffix_test_path) is False
