from datetime import datetime
from pathlib import Path
import pytest
import logging


def pytest_addoption(parser):
    parser.addoption(
        "--heal", action="store_true", default=False, help="Enable AI self-healing",
    )
    parser.addoption(
        "--no-report", action="store_true", default=False, help="Disable Report Generation",
    )


def pytest_configure(config):
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Check if the 'htmlpath' attribute exists or not to avoid AttributeError
    htmlpath = getattr(config.option, "htmlpath", None)
    no_report = config.getoption("--no-report")

    if not htmlpath and not no_report:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_dir = Path(f"test_results/{timestamp}")
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "report.html"
        config.option.htmlpath = str(report_path)
        config.option.self_contained_html = True


@pytest.fixture(scope="session")
def heal_enabled(request):
    return request.config.getoption("--heal")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if hasattr(item, "callspec"):
        url = item.callspec.params.get("page", "")
        page_name = url.split("/")[-1] if "/" in str(url) else "Unknown"
        report.page_version = page_name


def pytest_html_results_table_header(cells):
    """
    Customize HTML report table to include the header 'Page Version'. Runs after all test cases.
    """

    cells.insert(2, "<th>Page Version</th>")
    cells.pop()


def pytest_html_results_table_row(report, cells):
    """
    Update the page version data for each test. Runs after all test cases.
    """

    page_version = getattr(report, "page_version", "N/A")
    cells.insert(2, f"<td>{page_version}</td>")
    cells.pop()