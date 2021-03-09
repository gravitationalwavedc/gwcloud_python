from gwcloud_python import __version__
import requests


def test_version():
    assert __version__ == '0.1.0'

def test_gwcloud(requests_mock):
    requests_mock.get("https://test.com", json={'data': 'some data'})
    assert requests.get("https://test.com").text == {'data': 'some data'}