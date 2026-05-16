def days_ago(n: int) -> str:
    if n == 0:
        return "сегодня"
    if n == 1:
        return "вчера"
    last_digit = n % 10
    last_two = n % 100
    if 10 <= last_two <= 20:
        return f"{n} дней назад"
    if last_digit == 1:
        return f"{n} день назад"
    if last_digit in (2, 3, 4):
        return f"{n} дня назад"
    return f"{n} дней назад"


def days_word(n: int) -> str:
    last_digit = n % 10
    last_two = n % 100
    if 10 <= last_two <= 20:
        return "дней"
    if last_digit == 1:
        return "день"
    if last_digit in (2, 3, 4):
        return "дня"
    return "дней"
