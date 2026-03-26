from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class ParsedLine:
    transaction_type_id: int
    occurred_at: datetime
    amount: Decimal
    cpf: str
    card: str
    store_owner: str
    store_name: str


class CNABParseError(Exception):
    def __init__(self, line_number: int, reason: str):
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"Linha {line_number}: {reason}")


def parse_line(raw: str, line_number: int) -> ParsedLine:
    try:
        t_type = int(raw[0])
    except ValueError:
        raise CNABParseError(line_number, f"Tipo de transação inválido: '{raw[0]}'")

    date_str = raw[1:9]  
    time_str = raw[42:48]  

    try:
        occurred_at = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
    except ValueError:
        raise CNABParseError(line_number, f"Data/hora inválida: '{date_str}' '{time_str}'")

    try:
        amount = Decimal(raw[9:19]) / Decimal("100.00")
    except Exception:
        raise CNABParseError(line_number, f"Valor inválido: '{raw[9:19]}'")

    return ParsedLine(
        transaction_type_id=t_type,
        occurred_at=occurred_at,
        amount=amount,
        cpf=raw[19:30].strip(),
        card=raw[30:42].strip(),
        store_owner=raw[48:62].strip(),
        store_name=raw[62:81].strip(),
    )


def parse_cnab(content: str) -> tuple[list[ParsedLine], list[CNABParseError]]:
    lines = content.splitlines()
    parsed: list[ParsedLine] = []
    errors: list[CNABParseError] = []

    for i, line in enumerate(lines, start=1):
        stripped = line.rstrip("\n\r")
        if not stripped:
            continue
        try:
            parsed.append(parse_line(stripped, i))
        except CNABParseError as e:
            errors.append(e)

    return parsed, errors
