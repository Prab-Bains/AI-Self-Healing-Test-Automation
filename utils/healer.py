import logging
from langchain_ollama import OllamaLLM


logger = logging.getLogger(__name__)
llm = OllamaLLM(model="mistral", temperature=0, num_predict=20)


def smart_click(page, selector, heal_enabled=False):
    try:
        page.click(selector, timeout=5000)
    except Exception as e:
        if not heal_enabled:
            logger.error(f"Action failed on {selector}. Healing disabled.")
            raise e

        logger.warning(f"Selector '{selector}' failed. Attempting AI healing...")
        new_selector = perform_ai_healing(page, selector)

        if new_selector and "none" not in new_selector.lower():
            logger.info(f"Retrying with new selector: {new_selector}")
            try:
                page.click(new_selector)
            except Exception:
                logger.error(f"AI-healed click FAILED for {new_selector}")
                raise Exception(f"Healing failed: Suggested selector {new_selector} was not found.")
        else:
            logger.error("AI could not find a suitable replacement")
            raise e


def smart_locator(page, selector, heal_enabled=False):
    """
    Checks if a locator is valid. If it fails, attempts to heal and
    returns a new locator.
    """
    try:
        loc = page.locator(selector)
        loc.wait_for(state="attached", timeout=5000)
        return loc
    except Exception as e:
        logger.warning(f"Failed to find selector '{selector}'")
        if not heal_enabled:
            logger.error(f"Locator failed on {selector}. Healing disabled.")
            raise Exception(f"Locator failed. Please Fix test or re-run with healing enabled.")

        logger.warning(f"Attempting AI healing...")
        new_selector = perform_ai_healing(page, selector)

        if new_selector and "none" not in new_selector.lower():
            logger.info(f"Retrying with new selector: {new_selector}")
            try:
                healed_locator = page.locator(new_selector)
                healed_locator.wait_for(state="attached", timeout=3000)
                return healed_locator
            except Exception:
                logger.error(f"Attempted to find '{new_selector}', but it also failed.")
                raise Exception(f"Healing failed: Suggested selector {new_selector} was not found.")
        else:
            logger.error(f"AI could not find a suitable replacement for {selector}")
            raise e


def smart_fill(page, selector, value, heal_enabled=False):
    element = smart_locator(page, selector, heal_enabled)
    element.fill(value)


def perform_ai_healing(page, selector):
    dom_snapshot = page.inner_html("body")

    prompt = f"""
    ROLE: Expert Playwright Automation Engineer.

    TASK:
    The selector '{selector}' is no longer valid.
    Find the BEST replacement selector for the SAME element.

    HTML CONTEXT:
    ---
    {dom_snapshot}
    ---

    MATCHING STRATEGY:

    You are trying to locate the SAME element, not a specific button.

    Use these signals from the original selector:

    1. Element type (button, input, a, p, h1, etc.)
    2. Text content (visible text)
    3. Attributes:
       - id
       - name
       - data-testid
       - placeholder
       - aria-label
       - role
       - type
    4. Position or hierarchy if needed.

    SELECTION RULES (priority order):

    1. #id
    2. [data-testid='value']
    3. [name='value']
    4. [placeholder='value']
    5. [aria-label='value']
    6. role-based locator
    7. text-based locator

    NONE RULE:

    Return NONE ONLY if no element in the HTML reasonably matches the original element.

    STRICT OUTPUT:

    Return ONLY the selector string.
    No explanation.
    No markdown.

    ORIGINAL SELECTOR:
    {selector}

    OUTPUT:
    """

    try:
        response = llm.invoke(prompt).strip()
        healed_locator = response.replace("`", "")
        logger.info(f"HEALED LOCATOR {healed_locator}")
        logger.info(f"CLEANED HEALED LOCATOR {clean_llm_response(healed_locator)}")
        return clean_llm_response(healed_locator)
    except Exception as llm_err:
        logger.error(f"LLM Call failed: {llm_err}")
        return None


def clean_llm_response(raw_response):
    """
    Cleans the LLM response to ensure it's a valid Playwright selector.
    """
    # 1. Remove whitespace and common Markdown characters
    clean_response = raw_response.strip().replace("`", "").replace("'", "").replace('"', "")

    # If response is given in this format: [button-submit]
    # Assume it's meant to be an ID and format it like: #button-submit
    if clean_response.startswith("[") and clean_response.endswith("]"):
        selector = clean_response[1:-1]
        clean_response = f"#{selector}"

    return clean_response