import pytest
from decimal import Decimal
from datetime import datetime

from app.services.parsers import parse_line, parse_cnab, CNABParseError

VALID_LINE = "3201903010000014200096206760174753830274CP154702JOSE COSTA    MERCADO DA AVENIDA "


def test_parse_valid_line():
    result = parse_line(VALID_LINE, 1)
    assert result.transaction_type_id == 3
    assert result.amount == Decimal("142.00")
    assert result.occurred_at == datetime(2019, 3, 1, 15, 47, 2)
    assert result.cpf == "09620676017"
    assert result.store_name.strip() == "MERCADO DA AVENIDA"


def test_parse_type_1():
    line = "1" + VALID_LINE[1:]
    result = parse_line(line, 1)
    assert result.transaction_type_id == 1


def test_parse_type_9():
    line = "9" + VALID_LINE[1:]
    result = parse_line(line, 1)
    assert result.transaction_type_id == 9


def test_amount_divided_by_100():
    line = VALID_LINE[:9] + "0000000100" + VALID_LINE[19:]
    result = parse_line(line, 1)
    assert result.amount == Decimal("1.00")


def test_line_too_short_raises():
    with pytest.raises(CNABParseError) as exc_info:
        parse_line("3201903010000014200", 5)
    assert exc_info.value.line_number == 5


def test_invalid_type_raises():
    line = "X" + VALID_LINE[1:]
    with pytest.raises(CNABParseError):
        parse_line(line, 1)


def test_unknown_type_raises():
    line = "0" + VALID_LINE[1:]
    with pytest.raises(CNABParseError):
        parse_line(line, 1)


def test_parse_cnab_multiple_lines():
    content = VALID_LINE + "\n" + VALID_LINE.replace("3", "1", 1) + "\n"
    parsed, errors = parse_cnab(content)
    assert len(parsed) == 2
    assert len(errors) == 0


def test_parse_cnab_skips_empty_lines():
    content = "\n" + VALID_LINE + "\n\n"
    parsed, errors = parse_cnab(content)
    assert len(parsed) == 1


def test_parse_cnab_collects_errors():
    bad_line = "X" * 81
    content = VALID_LINE + "\n" + bad_line + "\n" + VALID_LINE + "\n"
    parsed, errors = parse_cnab(content)
    assert len(parsed) == 2
    assert len(errors) == 1
    assert errors[0].line_number == 2
