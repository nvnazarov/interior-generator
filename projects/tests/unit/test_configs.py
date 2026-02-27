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
        "postgres": {
            "db": "postgres",
            "host": "127.0.0.1",
            "port": 5432,
            "user": "postgres",
            "password": "",
            "password_file": None,
        },
        "general": {
            "projects_limit": 20,
            "plans_limit": 20,
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
            "PROJECTS__API__HOST": "0.0.0.0",
            "PROJECTS__API__PORT": "80",
            "PROJECTS__API__HEADER_FOR_ACCOUNT_ID": "test",
            "PROJECTS__GENERAL__PLANS_LIMIT": "10",
            "PROJECTS__GENERAL__PROJECTS_LIMIT": "15",
            "PROJECTS__POSTGRES__HOST": "test",
            "PROJECTS__POSTGRES__PORT": "5433",
            "PROJECTS__POSTGRES__DB": "test",
            "PROJECTS__POSTGRES__USER": "test",
            "PROJECTS__POSTGRES__PASSWORD": "test",
            "PROJECTS__LOGGING__LEVEL": "ERROR",
        }
    )
    config = RootConfig()
    assert config.model_dump() == {
        "api": {
            "host": "0.0.0.0",
            "port": 80,
            "header_for_account_id": "test",
        },
        "postgres": {
            "db": "test",
            "host": "test",
            "port": 5433,
            "user": "test",
            "password": "test",
            "password_file": None,
        },
        "general": {
            "projects_limit": 15,
            "plans_limit": 10,
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
    os.environ.setdefault("PROJECTS__POSTGRES__PASSWORD_FILE", password_file.as_posix())
    config = RootConfig()
    assert config.postgres.password == "test"
    assert config.postgres.password_file == password_file.as_posix()
