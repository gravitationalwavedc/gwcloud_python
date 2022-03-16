import pytest
from gwcloud_python.utils import to_snake_case, to_camel_case, convert_dict_keys, rename_dict_keys


@pytest.fixture
def snake_case():
    return [
        'single',
        'short_string',
        'a_much_longer_test_string',
        'test_key'
    ]


@pytest.fixture
def camel_case():
    return [
        'single',
        'shortString',
        'aMuchLongerTestString',
        'testKey'
    ]


@pytest.fixture
def snake_case_dict(snake_case):
    return {
        snake_case[0]: 0,
        snake_case[1]: 1,
        snake_case[2]: 2,
        snake_case[3]: [
            snake_case[0],
            {snake_case[2]: 2}
        ],
        snake_case[3]: {
            snake_case[0]: 0,
            snake_case[1]: 1,
            snake_case[2]: 2,
        }
    }


@pytest.fixture
def snake_case_renamed_dict(snake_case):
    renamed_map = {snake_case[2]: 'renamed'}
    renamed_dict = {
        snake_case[0]: 0,
        snake_case[1]: 1,
        'renamed': 2,
        snake_case[3]: [
            snake_case[0],
            {'renamed': 2}
        ],
        snake_case[3]: {
            snake_case[0]: 0,
            snake_case[1]: 1,
            'renamed': 2,
        }
    }
    return renamed_map, renamed_dict


@pytest.fixture
def camel_case_dict(camel_case):
    return {
        camel_case[0]: 0,
        camel_case[1]: 1,
        camel_case[2]: 2,
        camel_case[3]: [
            camel_case[0],
            {camel_case[2]: 2}
        ],
        camel_case[3]: {
            camel_case[0]: 0,
            camel_case[1]: 1,
            camel_case[2]: 2,
        }
    }


@pytest.fixture
def camel_case_renamed_dict(camel_case):
    renamed_map = {camel_case[2]: 'renamed'}
    renamed_dict = {
        camel_case[0]: 0,
        camel_case[1]: 1,
        'renamed': 2,
        camel_case[3]: [
            camel_case[0],
            {'renamed': 2}
        ],
        camel_case[3]: {
            camel_case[0]: 0,
            camel_case[1]: 1,
            'renamed': 2,
        }
    }
    return renamed_map, renamed_dict


def test_to_snake_case(snake_case, camel_case):
    for snake, camel in zip(snake_case, camel_case):
        assert to_snake_case(camel) == snake


def test_to_camel_case(snake_case, camel_case):
    for snake, camel in zip(snake_case, camel_case):
        assert to_camel_case(snake) == camel


def test_renamed_dict_keys(snake_case_dict, snake_case_renamed_dict, camel_case_dict, camel_case_renamed_dict):
    assert rename_dict_keys(snake_case_dict, snake_case_renamed_dict[0]) == snake_case_renamed_dict[1]
    assert rename_dict_keys(camel_case_dict, camel_case_renamed_dict[0]) == camel_case_renamed_dict[1]


def test_convert_dict_keys(snake_case_dict, snake_case_renamed_dict, camel_case_dict, camel_case_renamed_dict):
    converted_snake_case_dict = convert_dict_keys(snake_case_dict, reverse=True)
    converted_camel_case_dict = convert_dict_keys(camel_case_dict)

    renamed_snake_case_dict = convert_dict_keys(snake_case_dict, key_map=snake_case_renamed_dict[0], reverse=True)
    renamed_camel_case_dict = convert_dict_keys(camel_case_dict, key_map=camel_case_renamed_dict[0])

    # Can convert
    assert converted_camel_case_dict == snake_case_dict
    assert converted_snake_case_dict == camel_case_dict

    # Conversion is reversible
    assert convert_dict_keys(converted_camel_case_dict, reverse=True) == camel_case_dict
    assert convert_dict_keys(converted_snake_case_dict) == snake_case_dict

    # Can convert and rename from key map
    assert renamed_camel_case_dict == snake_case_renamed_dict[1]
    assert renamed_snake_case_dict == camel_case_renamed_dict[1]


    