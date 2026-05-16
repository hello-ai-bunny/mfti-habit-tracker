from app.format import days_ago, days_word


def test_days_ago_today():
    assert days_ago(0) == "сегодня"


def test_days_ago_yesterday():
    assert days_ago(1) == "вчера"


def test_days_ago_few():
    assert days_ago(2) == "2 дня назад"
    assert days_ago(4) == "4 дня назад"


def test_days_ago_many():
    assert days_ago(5) == "5 дней назад"
    assert days_ago(7) == "7 дней назад"


def test_days_ago_teens():
    # 11-14 → "дней" а не "день/дня"
    assert days_ago(11) == "11 дней назад"
    assert days_ago(14) == "14 дней назад"
    assert days_ago(15) == "15 дней назад"


def test_days_ago_compound():
    assert days_ago(21) == "21 день назад"
    assert days_ago(22) == "22 дня назад"
    assert days_ago(25) == "25 дней назад"


def test_days_word():
    assert days_word(0) == "дней"
    assert days_word(1) == "день"
    assert days_word(2) == "дня"
    assert days_word(5) == "дней"
    assert days_word(11) == "дней"
    assert days_word(21) == "день"
