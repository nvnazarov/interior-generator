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
        },
        "postgres": {
            "db": "postgres",
            "host": "127.0.0.1",
            "port": 5432,
            "user": "postgres",
            "password": "",
            "password_file": None,
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
            "CATALOG__POSTGRES__HOST": "test",
            "CATALOG__POSTGRES__PORT": "5433",
            "CATALOG__POSTGRES__DB": "test",
            "CATALOG__POSTGRES__USER": "test",
            "CATALOG__POSTGRES__PASSWORD": "test",
            "CATALOG__LOGGING__LEVEL": "ERROR",
        }
    )
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "0.0.0.0",
            "port": 80,
        },
        "postgres": {
            "db": "test",
            "host": "test",
            "port": 5433,
            "user": "test",
            "password": "test",
            "password_file": None,
        },
        "logging": {
            "level": "ERROR",
        },
    }


@pytest.mark.unit
def test_root_config_password_file(tmp_path: pathlib.Path):
    os.environ.clear()
    password_file = tmp_path / "password.txt"
    password_file.write_text("test")
    os.environ.setdefault("CATALOG__POSTGRES__PASSWORD_FILE", password_file.as_posix())
    config = RootConfig()
    assert config.postgres.password == "test"
    assert config.postgres.password_file == password_file.as_posix()
