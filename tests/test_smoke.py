from playwright.sync_api import Page, expect


def test_booking_page_is_available(page: Page, base_url: str):
    """Infrastructure check only; does not check booking business rules."""
    response = page.goto(base_url, wait_until="domcontentloaded")
    assert response is not None and response.ok, "Demo page did not load successfully"
    expect(page.get_by_role("button", name="Забронировать")).to_be_visible()
