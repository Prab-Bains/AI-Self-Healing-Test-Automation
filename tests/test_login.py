import logging
import pytest
from playwright.sync_api import expect
from utils.constants import *
from utils.healer import smart_click, smart_locator, smart_fill

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def setup_page(page, request, heal_enabled):
    # Fallback to PAGE1 if no parameter is passed
    url = getattr(request, "param", PAGES["V1"])
    page.heal_enabled = heal_enabled
    logger.info(f"--- STARTING TEST ON: {url.split('/')[-1]} (Healing: {heal_enabled}) ---")
    page.goto(url)
    yield page


@pytest.mark.parametrize("setup_page", [PAGES["V1"], PAGES["V2"], PAGES["V3"]], indirect=True)
def test_username_input_exists(setup_page):
    logger.info("STARTING TEST: test_username_input_exists")
    logger.info("TEST STEP 1: Verify username input visibility and placeholder text")
    username = smart_locator(setup_page, Selectors.USERNAME_FIELD, heal_enabled=setup_page.heal_enabled)
    expect(username).to_be_visible()
    expect(username).to_have_attribute("placeholder", "Username")


@pytest.mark.parametrize("setup_page", [PAGES["V1"], PAGES["V2"], PAGES["V3"]], indirect=True)
def test_password_input_exists(setup_page):
    logger.info("STARTING TEST: test_password_input_exists")
    logger.info("TEST STEP 1: Verify password input visibility and placeholder text")
    password = smart_locator(setup_page, Selectors.PASSWORD_FIELD, heal_enabled=setup_page.heal_enabled)
    expect(password).to_be_visible()
    expect(password).to_have_attribute("placeholder", "Password")


@pytest.mark.parametrize("setup_page", [PAGES["V1"], PAGES["V2"], PAGES["V3"]], indirect=True)
def test_login_button_exists(setup_page):
    logger.info("STARTING TEST: test_login_button_exists")
    logger.info("TEST STEP 1: Verify login button visibility and placeholder text")
    button = smart_locator(setup_page, Selectors.LOGIN_BUTTON, heal_enabled=setup_page.heal_enabled)
    expect(button).to_be_visible()
    expect(button).to_have_text("Log In")


@pytest.mark.parametrize("setup_page", [PAGES["V1"], PAGES["V2"], PAGES["V3"]], indirect=True)
def test_empty_username(setup_page):
    logger.info("STARTING TEST: test_empty_username")
    logger.info("TEST STEP 1: Enter password only")
    smart_fill(setup_page, Selectors.PASSWORD_FIELD, "testPassword", heal_enabled=setup_page.heal_enabled)

    logger.info("TEST STEP 2: Click Login")
    smart_click(setup_page, Selectors.LOGIN_BUTTON, heal_enabled=setup_page.heal_enabled)

    logger.info("TEST STEP 3: Verify Error Message and Color")
    message = smart_locator(setup_page, Selectors.MESSAGE_TEXT, heal_enabled=setup_page.heal_enabled)
    expect(message).to_have_text("Please enter your username")
    expect(message).to_have_attribute("style", "color: red;")


@pytest.mark.parametrize("setup_page", [PAGES["V1"], PAGES["V2"], PAGES["V3"]], indirect=True)
def test_empty_password(setup_page):
    logger.info("STARTING TEST: test_empty_password")
    logger.info("TEST STEP 1: Enter username only")
    smart_fill(setup_page, Selectors.USERNAME_FIELD, "testUsername", heal_enabled=setup_page.heal_enabled)

    logger.info("TEST STEP 2: Click Login")
    smart_click(setup_page, Selectors.LOGIN_BUTTON, heal_enabled=setup_page.heal_enabled)

    logger.info("TEST STEP 3: Verify Password Error Message")
    message = smart_locator(setup_page, Selectors.MESSAGE_TEXT, heal_enabled=setup_page.heal_enabled)
    expect(message).to_have_text("Please enter your password", ignore_case=True)
    expect(message).to_have_attribute("style", "color: red;")


@pytest.mark.parametrize("setup_page", [PAGES["V1"], PAGES["V2"], PAGES["V3"]], indirect=True)
def test_empty_username_and_password(setup_page):
    logger.info("STARTING TEST: test_empty_username_and_password")
    logger.info("TEST STEP 1: Click Login Without Username or Password")
    smart_click(setup_page, Selectors.LOGIN_BUTTON, heal_enabled=setup_page.heal_enabled)

    logger.info("TEST STEP 2: Verify Password Error Message")
    message = smart_locator(setup_page, Selectors.MESSAGE_TEXT, heal_enabled=setup_page.heal_enabled)
    expect(message).to_have_text("Please enter your username and password", ignore_case=True)
    expect(message).to_have_attribute("style", "color: red;")


@pytest.mark.parametrize("setup_page", [PAGES["V1"], PAGES["V2"], PAGES["V3"]], indirect=True)
def test_successful_login(setup_page):
    logger.info("STARTING TEST: test_successful_login")
    logger.info("TEST STEP 1: Enter valid credentials")
    smart_fill(setup_page, Selectors.USERNAME_FIELD, "testUsername", heal_enabled=setup_page.heal_enabled)
    smart_fill(setup_page, Selectors.PASSWORD_FIELD, "testPassword", heal_enabled=setup_page.heal_enabled)

    logger.info("TEST STEP 2: Click Login")
    smart_click(setup_page, Selectors.LOGIN_BUTTON, heal_enabled=setup_page.heal_enabled)

    logger.info("TEST STEP 3: Verify Success Message")
    message = smart_locator(setup_page, Selectors.MESSAGE_TEXT, heal_enabled=setup_page.heal_enabled)
    expect(message).to_have_text("Successful login", ignore_case=True)
    expect(message).to_have_attribute("style", "color: green;")
