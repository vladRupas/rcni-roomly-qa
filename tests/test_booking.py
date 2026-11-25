from datetime import date, timedelta

import pytest
from playwright.sync_api import Page, expect


def fill_valid_booking(page: Page) -> str:
    """Fill a deterministic booking for a future calendar day."""
    booking_date = (date.today() + timedelta(days=1)).isoformat()
    page.get_by_label("Переговорная *").select_option("medium")
    page.get_by_label("Дата *").fill(booking_date)
    page.get_by_label("Начало *").fill("10:00")
    page.get_by_label("Окончание *").fill("11:00")
    page.get_by_label("Участники *").fill("6")
    page.get_by_label("Ваше имя *").fill("QA Tester")
    page.get_by_label("Рабочая почта *").fill("qa@example.org")
    return booking_date


def test_successful_booking_and_no_persistence(page: Page, base_url: str):
    page.goto(base_url, wait_until="domcontentloaded")
    booking_date = fill_valid_booking(page)

    page.get_by_role("button", name="Забронировать").click()

    status = page.locator("#form-status")
    expect(status).to_contain_text("Бронирование создано.")
    expect(status).to_contain_text(f"Средняя, {booking_date}, 10:00–11:00 · QA Tester")

    page.reload(wait_until="domcontentloaded")
    expect(page.locator("#room")).to_have_value("")
    expect(page.locator("#name")).to_have_value("")
    expect(page.locator("#email")).to_have_value("")
    expect(page.locator("#form-status")).to_be_empty()


def test_room_capacity_is_validated(page: Page, base_url: str):
    page.goto(base_url, wait_until="domcontentloaded")
    booking_date = (date.today() + timedelta(days=1)).isoformat()
    page.get_by_label("Переговорная *").select_option("small")
    page.get_by_label("Дата *").fill(booking_date)
    page.get_by_label("Начало *").fill("10:00")
    page.get_by_label("Окончание *").fill("11:00")
    page.get_by_label("Участники *").fill("5")
    page.get_by_label("Ваше имя *").fill("QA Tester")
    page.get_by_label("Рабочая почта *").fill("qa@example.org")

    page.get_by_role("button", name="Забронировать").click()

    expect(page.locator('[data-error-for="participants"]')).to_contain_text("максимум 4")
    expect(page.locator("#form-status")).to_contain_text("Проверьте")


@pytest.mark.xfail(
    strict=True,
    reason="BUG-01: бронирование короче 30 минут принимается",
    raises=AssertionError,
)
def test_booking_shorter_than_30_minutes_is_rejected(page: Page, base_url: str):
    page.goto(base_url, wait_until="domcontentloaded")
    booking_date = (date.today() + timedelta(days=1)).isoformat()
    page.get_by_label("Переговорная *").select_option("small")
    page.get_by_label("Дата *").fill(booking_date)
    page.get_by_label("Начало *").fill("10:00")
    page.get_by_label("Окончание *").fill("10:10")
    page.get_by_label("Участники *").fill("2")
    page.get_by_label("Ваше имя *").fill("QA Tester")
    page.get_by_label("Рабочая почта *").fill("qa@example.org")

    page.get_by_role("button", name="Забронировать").click()

    # Check expected behavior. The current page incorrectly shows a success message.
    expect(page.locator("#form-status")).to_have_class("form-status error")
    expect(page.locator('[data-error-for="endTime"]')).to_contain_text("30 минут")
