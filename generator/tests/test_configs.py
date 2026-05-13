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
            "account_header": "x-account-id",
        },
        "gateway": {
            "base_url": "",
        },
        "postgres": {
            "db": "postgres",
            "host": "127.0.0.1",
            "port": 5432,
            "user": "postgres",
            "password": "",
            "password_file": None,
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
            "GENERATOR__API__ACCOUNT_HEADER": "test",
            "GENERATOR__OPENAI__API_KEY": "test",
            "GENERATOR__OPENAI__BASE_URL": "test",
            "GENERATOR__POSTGRES__HOST": "test",
            "GENERATOR__POSTGRES__PORT": "5433",
            "GENERATOR__POSTGRES__USER": "test",
            "GENERATOR__POSTGRES__PASSWORD": "test",
            "GENERATOR__POSTGRES__DB": "test",
            "GENERATOR__GATEWAY__BASE_URL": "http://private-gateway/api",
            "GENERATOR__LOGGING__LEVEL": "ERROR",
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
            "base_url": "http://private-gateway/api",
        },
        "postgres": {
            "db": "test",
            "host": "test",
            "port": 5433,
            "user": "test",
            "password": "test",
            "password_file": None,
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
