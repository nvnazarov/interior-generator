import os
from pathlib import Path

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
        "minio": {
            "host": "127.0.0.1",
            "port": 9000,
            "access_key": "",
            "secret_key": "",
            "secret_key_file": None,
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
            "ASSETS__API__HOST": "0.0.0.0",
            "ASSETS__API__PORT": "80",
            "ASSETS__MINIO__HOST": "test",
            "ASSETS__MINIO__PORT": "9090",
            "ASSETS__MINIO__ACCESS_KEY": "test",
            "ASSETS__MINIO__SECRET_KEY": "test",
            "ASSETS__LOGGING__LEVEL": "ERROR",
        }
    )
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "0.0.0.0",
            "port": 80,
        },
        "minio": {
            "host": "test",
            "port": 9090,
            "access_key": "test",
            "secret_key": "test",
            "secret_key_file": None,
        },
        "logging": {
            "level": "ERROR",
        },
    }


@pytest.mark.unit
def test_root_config_secret_key_file(tmp_path: Path):
    os.environ.clear()
    password_file = tmp_path / "password.txt"
    password_file.write_text("test")
    os.environ.setdefault("ASSETS__MINIO__SECRET_KEY_FILE", password_file.as_posix())
    config = RootConfig()
    assert config.minio.secret_key == "test"
    assert config.minio.secret_key_file == password_file.as_posix()
