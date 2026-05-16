from datetime import date, timedelta

from app.stats import (
    build_heatmap,
    current_streak,
    done_in_last_n_days,
    longest_streak,
)


TODAY = date(2026, 5, 17)


def days_back(n: int) -> set[date]:
    """Множество последних n дней, включая сегодня."""
    return {TODAY - timedelta(days=i) for i in range(n)}


def test_streak_empty():
    assert current_streak(set(), TODAY) == 0


def test_streak_only_today():
    assert current_streak({TODAY}, TODAY) == 1


def test_streak_today_and_yesterday():
    assert current_streak({TODAY, TODAY - timedelta(days=1)}, TODAY) == 2


def test_streak_three_consecutive():
    assert current_streak(days_back(3), TODAY) == 3


def test_streak_zero_if_today_missing():
    """Строгое правило: если сегодня не отмечено — стрик 0."""
    yesterday_and_before = days_back(3) - {TODAY}
    assert current_streak(yesterday_and_before, TODAY) == 0


def test_streak_breaks_on_gap():
    logged = {
        TODAY,
        TODAY - timedelta(days=1),
        TODAY - timedelta(days=3),  
        TODAY - timedelta(days=4),
    }
    assert current_streak(logged, TODAY) == 2



def test_longest_streak_empty():
    assert longest_streak(set()) == 0


def test_longest_streak_one_day():
    assert longest_streak({TODAY}) == 1


def test_longest_streak_consecutive():
    assert longest_streak(days_back(5)) == 5


def test_longest_streak_with_gap():
    logged = days_back(3) | {TODAY - timedelta(days=10), TODAY - timedelta(days=11)}
    assert longest_streak(logged) == 3



def test_done_in_last_n_all_done():
    assert done_in_last_n_days(days_back(7), TODAY, 7) == 7


def test_done_in_last_n_some():
    logged = {TODAY, TODAY - timedelta(days=2), TODAY - timedelta(days=5)}
    assert done_in_last_n_days(logged, TODAY, 7) == 3


def test_done_in_last_n_outside_window_ignored():
    logged = {TODAY - timedelta(days=30)}
    assert done_in_last_n_days(logged, TODAY, 7) == 0



def test_heatmap_structure():
    weeks = build_heatmap(set(), TODAY, days_back=119)
    assert 17 <= len(weeks) <= 18
    for week in weeks:
        assert len(week) == 7


def test_heatmap_today_marked():
    weeks = build_heatmap(set(), TODAY, days_back=30)
    today_cells = [d for w in weeks for d in w if d["is_today"]]
    assert len(today_cells) == 1
    assert today_cells[0]["date"] == TODAY


def test_heatmap_logged_dates():
    logged = {TODAY, TODAY - timedelta(days=5)}
    weeks = build_heatmap(logged, TODAY, days_back=30)
    logged_cells = [d for w in weeks for d in w if d["logged"]]
    assert len(logged_cells) == 2
    assert {c["date"] for c in logged_cells} == logged


def test_heatmap_out_of_range_cells():
    """Ячейки до start_date или после today должны иметь in_range=False."""
    weeks = build_heatmap(set(), TODAY, days_back=10)
    out_of_range = [d for w in weeks for d in w if not d["in_range"]]
    assert len(out_of_range) > 0
    for cell in out_of_range:
        assert not cell["logged"]
