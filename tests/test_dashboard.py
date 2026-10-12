"""Dashboard helpers, rendered interactions, and local server startup."""

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from streamlit.testing.v1 import AppTest

from payment_ops.samples.payments import SYNTHETIC_PAYMENTS
from payment_ops.services.decision_engine import PaymentDecision
from payment_ops.ui.app import load_payments
from payment_ops.ui.helpers import aggregate_metrics, filter_payments, format_amount, payment_rows


APP_PATH = Path(__file__).resolve().parents[1] / "src/payment_ops/ui/app.py"


def test_aggregate_metrics() -> None:
    metrics = aggregate_metrics(load_payments())
    assert metrics == {
        "total_payments": 20, "total_value": Decimal("300107.02"), "excluded_amounts": 3,
        "decision_counts": {
            PaymentDecision.READY_FOR_PROCESSING: 4,
            PaymentDecision.MANUAL_REVIEW: 6,
            PaymentDecision.REJECTED: 10,
        },
    }


def test_empty_metrics_and_filter() -> None:
    metrics = aggregate_metrics([])
    assert metrics["total_value"] == Decimal("0")
    assert metrics["total_payments"] == 0
    assert filter_payments([], None) == []


@pytest.mark.parametrize("decision,count", [(None, 20), (PaymentDecision.READY_FOR_PROCESSING, 4), (PaymentDecision.MANUAL_REVIEW, 6), (PaymentDecision.REJECTED, 10)])
def test_filter(decision: PaymentDecision | None, count: int) -> None:
    filtered = filter_payments(load_payments(), decision)
    assert len(filtered) == count
    assert all(decision is None or result.decision is decision for _, result in filtered)


@pytest.mark.parametrize("value,formatted", [(None, "Missing"), (Decimal("NaN"), "Invalid amount"), (Decimal("Infinity"), "Invalid amount"), ("100", "Invalid amount"), (Decimal("1234.56"), "$1,234.56"), (Decimal("-1"), "$-1.00")])
def test_amount_formatting(value: object, formatted: str) -> None:
    assert format_amount(value) == formatted


def test_metric_exclusions_do_not_drop_instructions() -> None:
    payment, result = load_payments()[0]
    entries = [(replace(payment, amount=value), result) for value in (None, Decimal("NaN"), Decimal("Infinity"), Decimal("-1"), Decimal("0"), Decimal("0.01"))]
    metrics = aggregate_metrics(entries)
    assert metrics["total_payments"] == 6
    assert metrics["excluded_amounts"] == 5
    assert metrics["total_value"] == Decimal("0.01")
    assert len(payment_rows(entries)) == 6


def test_initial_render_and_metrics() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    assert not app.exception
    assert app.title[0].value == "Payment Operations Intelligence Platform"
    assert [metric.value for metric in app.metric] == ["20", "$300,107.02", "4", "6", "10"]
    assert len(app.dataframe[0].value) == 20
    assert len(app.selectbox[1].options) == 20


@pytest.mark.parametrize("decision,count", [(PaymentDecision.READY_FOR_PROCESSING, 4), (PaymentDecision.MANUAL_REVIEW, 6), (PaymentDecision.REJECTED, 10)])
def test_filter_interaction(decision: PaymentDecision, count: int) -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    app.selectbox(key="selected_payment").select("SYNTHETIC-WIRE-UNAVAILABLE").run()
    app.selectbox(key="decision_filter").select(decision.value).run()
    assert not app.exception
    assert len(app.dataframe[0].value) == count
    assert len(app.selectbox(key="selected_payment").options) == count
    assert all(decision.value in value for value in app.dataframe[0].value["Final Decision"])
    assert app.metric[0].value == "20"


@pytest.mark.parametrize("payment", SYNTHETIC_PAYMENTS, ids=[payment.payment_id for payment in SYNTHETIC_PAYMENTS])
def test_selection_shows_service_result(payment) -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    app.selectbox(key="selected_payment").select(payment.payment_id).run()
    assert not app.exception
    expected = next(result for instruction, result in load_payments() if instruction.payment_id == payment.payment_id)
    message = (app.error if expected.decision is PaymentDecision.REJECTED else app.warning if expected.decision is PaymentDecision.MANUAL_REVIEW else app.success)[0].value
    assert expected.decision.value in message
    assert expected.primary_reason in message
    checks = app.dataframe[1].value
    assert len(checks) == 6
    for index, check in enumerate(expected.checks):
        assert check.status.value in checks.iloc[index]["Status"]
        assert checks.iloc[index]["Explanation"] == " ".join(check.reasons)
    assert all(reason in [element.value for element in app.markdown] for reason in expected.reasons)
    assert app.table[0].value.iloc[0]["Value"] == payment.payment_id


def test_safe_load_error(monkeypatch) -> None:
    def fail():
        raise RuntimeError("private internal details")
    monkeypatch.setattr("payment_ops.ui.app.load_payments", fail)
    app = AppTest.from_string("from payment_ops.ui.app import main\nmain()", default_timeout=20).run()
    assert not app.exception
    assert "could not be loaded" in app.error[0].value
    assert "private internal details" not in app.error[0].value
    assert len(app.metric) == 0


def test_streamlit_server_starts() -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(APP_PATH),
         "--server.headless=true", "--server.address=127.0.0.1", f"--server.port={port}",
         "--browser.gatherUsageStats=false"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            assert process.poll() is None, "Streamlit exited before startup."
            try:
                with urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1) as response:
                    assert response.status == 200
                    assert response.read() == b"ok"
                    return
            except (URLError, TimeoutError):
                time.sleep(0.1)
        pytest.fail("Streamlit did not become healthy within 20 seconds.")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
