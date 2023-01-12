def convert_to_decimals(decimal_places: int, number: long) -> float:
    return number / (10**decimal_places)


def convert_from_decimals(decimal_places: int, number: float) -> int:
    return number * (10**decimal_places)
