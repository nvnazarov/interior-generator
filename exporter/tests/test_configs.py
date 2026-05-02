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
            "account_header": "x-account-id",
        },
        "gateway": {
            "base_url": "",
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
            "EXPORTER__API__HOST": "0.0.0.0",
            "EXPORTER__API__PORT": "80",
            "EXPORTER__API__ACCOUNT_HEADER": "test",
            "EXPORTER__GATEWAY__BASE_URL": "test",
            "EXPORTER__LOGGING__LEVEL": "ERROR",
        }
    )
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "0.0.0.0",
            "port": 80,
            "account_header": "test",
        },
        "gateway": {
            "base_url": "test",
        },
        "logging": {
            "level": "ERROR",
        },
    }
