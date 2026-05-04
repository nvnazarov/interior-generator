import os

import pytest

from app.configs.root import RootConfig


@pytest.mark.unit
def test_default_root_config():
    os.environ.clear()
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "127.0.0.1",
            "port": 8080,
        },
        "elastic": {
            "host": "http://127.0.0.1:9200",
            "index": "catalog",
        },
        "logging": {
            "level": "INFO",
        },
    }


@pytest.mark.unit
def test_root_config():
    os.environ.clear()
    os.environ.update(
        {
            "CATALOG__API__HOST": "0.0.0.0",
            "CATALOG__API__PORT": "80",
            "CATALOG__ELASTIC__HOST": "http://elastic:9200",
            "CATALOG__ELASTIC__INDEX": "test-catalog",
            "CATALOG__LOGGING__LEVEL": "ERROR",
        }
    )
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "0.0.0.0",
            "port": 80,
        },
        "elastic": {
            "host": "http://elastic:9200",
            "index": "test-catalog",
        },
        "logging": {
            "level": "ERROR",
        },
    }
