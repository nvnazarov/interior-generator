import os
import pathlib

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
        "openai": {
            "api_key": "",
            "api_key_file": None,
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
            "GENERATOR__API__HOST": "0.0.0.0",
            "GENERATOR__API__PORT": "80",
            "GENERATOR__API__HEADER_FOR_ACCOUNT_ID": "test",
            "GENERATOR__OPENAI__API_KEY": "test",
            "GENERATOR__OPENAI__BASE_URL": "test",
            "GENERATOR__LOGGING__LEVEL": "ERROR",
        }
    )
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "0.0.0.0",
            "port": 80,
            "header_for_account_id": "test",
        },
        "openai": {
            "api_key": "test",
            "api_key_file": None,
            "base_url": "test",
        },
        "logging": {
            "level": "ERROR",
        },
    }


@pytest.mark.unit
def test_root_config_api_key_file(tmp_path: pathlib.Path):
    os.environ.clear()
    api_key_file = tmp_path / "key.txt"
    api_key_file.write_text("test")
    os.environ.setdefault("GENERATOR__OPENAI__API_KEY_FILE", api_key_file.as_posix())
    config = RootConfig()
    assert config.openai.api_key == "test"
    assert config.openai.api_key_file == api_key_file.as_posix()
