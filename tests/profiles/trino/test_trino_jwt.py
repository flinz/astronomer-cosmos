"Tests for the Trino profile."

import json
from unittest.mock import patch

import pytest
from airflow.models.connection import Connection

from cosmos.profiles import TrinoJWTProfileMapping


@pytest.fixture()
def mock_trino_conn():  # type: ignore
    """
    Mocks and returns an Airflow Trino connection.
    """
    conn = Connection(
        conn_id="my_trino_conn",
        conn_type="trino",
        host="my_host",
        port=8080,
        extra=json.dumps(
            {
                "jwt__token": "my_jwt_token",
            }
        ),
    )

    with patch("airflow.hooks.base.BaseHook.get_connection", return_value=conn):
        yield conn


def test_profile_args(
    mock_trino_conn: Connection,
) -> None:
    """
    Tests that the profile values get set correctly.
    """
    profile_mapping = TrinoJWTProfileMapping(
        mock_trino_conn.conn_id,
        profile_args={
            "database": "my_database",
            "schema": "my_schema",
        },
    )

    assert profile_mapping.profile == {
        "type": "trino",
        "method": "jwt",
        "host": "my_host",
        "port": 8080,
        "database": "my_database",
        "schema": "my_schema",
        "jwt_token": "{{ env_var('COSMOS_CONN_TRINO_JWT_TOKEN') }}",
    }


def test_profile_args_overrides(
    mock_trino_conn: Connection,
) -> None:
    """
    Tests that you can override the profile values.
    """
    profile_mapping = TrinoJWTProfileMapping(
        mock_trino_conn.conn_id,
        profile_args={
            "database": "my_database",
            "schema": "my_schema",
            "host": "my_host_override",
            "jwt_token": "my_jwt_token_override",
        },
    )

    assert profile_mapping.profile == {
        "type": "trino",
        "method": "jwt",
        "host": "my_host_override",
        "port": 8080,
        "database": "my_database",
        "schema": "my_schema",
        "jwt_token": "{{ env_var('COSMOS_CONN_TRINO_JWT_TOKEN') }}",
    }


def test_profile_env_vars(
    mock_trino_conn: Connection,
) -> None:
    """
    Tests that the environment variables get set correctly.
    """
    profile_mapping = TrinoJWTProfileMapping(
        mock_trino_conn.conn_id,
        profile_args={
            "database": "my_database",
            "schema": "my_schema",
        },
    )
    assert profile_mapping.env_vars == {
        "COSMOS_CONN_TRINO_JWT_TOKEN": "my_jwt_token",
    }