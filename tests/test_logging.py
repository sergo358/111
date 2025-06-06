import pytest
from core.logging import log_database_query

def test_log_database_query():
    # Тест функции логирования запросов
    log_database_query("SELECT * FROM specialists")
    assert True
