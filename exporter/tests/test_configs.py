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
            "header_for_account_id": "x-account-id",
        },
        "api_gateway": {
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
            "EXPORTER__API__HEADER_FOR_ACCOUNT_ID": "test",
            "EXPORTER__API_GATEWAY__BASE_URL": "test",
            "EXPORTER__LOGGING__LEVEL": "ERROR",
        }
    )
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "0.0.0.0",
            "port": 80,
            "header_for_account_id": "test",
        },
        "api_gateway": {
            "base_url": "test",
        },
        "logging": {
            "level": "ERROR",
        },
    }
