from uuid import uuid4
from typing import Dict

import requests
from playwright.sync_api import Page


def _build_unique_user() -> Dict[str, str]:
    suffix = uuid4().hex[:10]
    password = "ValidPass123!"
    return {
        "first_name": f"Test{suffix[:4]}",
        "last_name": f"User{suffix[4:8]}",
        "email": f"test.user.{suffix}@example.com",
        "username": f"user_{suffix}",
        "password": password,
        "confirm_password": password,
    }


def _goto(page: Page, base_url: str, path: str) -> None:
    page.goto(f"{base_url.rstrip('/')}/{path.lstrip('/')}", wait_until="networkidle")


def _expect_text(page: Page, selector: str, expected_substring: str) -> None:
    locator = page.locator(selector)
    locator.wait_for(state="visible")
    assert expected_substring in locator.inner_text()


def test_register_success(page: Page, fastapi_server: str) -> None:
    user = _build_unique_user()
    _goto(page, fastapi_server, "/register")

    page.fill("#username", user["username"])
    page.fill("#email", user["email"])
    page.fill("#first_name", user["first_name"])
    page.fill("#last_name", user["last_name"])
    page.fill("#password", user["password"])
    page.fill("#confirm_password", user["confirm_password"])
    page.click("button[type='submit']")

    _expect_text(page, "#successAlert", "Registration successful")
    page.wait_for_url(fastapi_server.rstrip('/') + "/login", timeout=5000)


def test_register_short_password_validation(page: Page, fastapi_server: str) -> None:
    user = _build_unique_user()
    _goto(page, fastapi_server, "/register")

    page.fill("#username", user["username"])
    page.fill("#email", user["email"])
    page.fill("#first_name", user["first_name"])
    page.fill("#last_name", user["last_name"])
    page.fill("#password", "Ab1")
    page.fill("#confirm_password", "Ab1")
    page.click("button[type='submit']")

    _expect_text(page, "#errorAlert", "Password must be at least 8 characters long")


def test_login_success(page: Page, fastapi_server: str) -> None:
    user = _build_unique_user()
    register_response = requests.post(f"{fastapi_server.rstrip('/')}/auth/register", json=user, timeout=15)
    assert register_response.status_code == 201, register_response.text

    _goto(page, fastapi_server, "/login")
    page.fill("#username", user["username"])
    page.fill("#password", user["password"])
    page.click("button[type='submit']")

    _expect_text(page, "#successAlert", "Login successful")
    page.wait_for_url(fastapi_server.rstrip('/') + "/dashboard", timeout=5000)
    token = page.evaluate("() => window.localStorage.getItem('access_token')")
    assert token, "Expected access token to be stored"


def test_login_invalid_password(page: Page, fastapi_server: str) -> None:
    user = _build_unique_user()
    register_response = requests.post(f"{fastapi_server.rstrip('/')}/auth/register", json=user, timeout=15)
    assert register_response.status_code == 201, register_response.text

    _goto(page, fastapi_server, "/login")
    page.fill("#username", user["username"])
    page.fill("#password", "WrongPass123!")
    page.click("button[type='submit']")

    _expect_text(page, "#errorAlert", "Invalid username or password")
