from api_collections import UserAPI
from constants import PHONE_NUMBER , TCMS_URL , TCMS_USERNAME , TCMS_PASSWORD
from common_functions import schema_validator, update_token_in_constants
import pytest
from tcms_api import TCMS
import TCMS_tools.tcms_maps as tcms_maps
import datetime

# TCMS setup
tcms_url = TCMS_URL
tcms_username = TCMS_USERNAME
tcms_password = TCMS_PASSWORD
rpc = TCMS(tcms_url, tcms_username, tcms_password).exec

runner_id = None  # Global variable for runner_id

# -------------------- helpers: TCMS reporting --------------------
def _get_case_id_in_run(run_id: int, case_summary: str) -> int:
    cases = rpc.TestRun.get_cases(run_id)
    for c in cases:
        if c.get("summary") == case_summary:
            return c["id"]
    raise RuntimeError(f"TestCase '{case_summary}' not found in run {run_id}")

def set_exec_status(case_summary: str, ok: bool):
    """Update execution status for a case in the active run."""
    case_id = _get_case_id_in_run(runner_id, case_summary)
    executions = rpc.TestExecution.filter({"run_id": runner_id, "case": case_id})
    if not executions:
        raise RuntimeError(f"No executions for case_id={case_id} in run_id={runner_id}")

    status_key = "PASSED" if ok else "FAILED"
    status_id = tcms_maps.EXECUTION_STATUSES[status_key]

    for e in executions:
        rpc.TestExecution.update(e["id"], {"status": status_id})
        print(f"[TCMS] {case_summary} -> Execution {e['id']} set to {status_key} ({status_id})")

# -------------------- create Test Run & add cases --------------------
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

test_run_data = {
    "summary": f"test_user_login_flow {now_str}",
    "plan": tcms_maps.TEST_PLANS["LEND_LOGIN_BACKEND"],
    "build": tcms_maps.BUILDS_BY_PRODUCT[str(tcms_maps.PRODUCTS["LEND_USER"])]["unspecified"],
    "manager": tcms_maps.USERS["dgstack"],
    "product": tcms_maps.PRODUCTS["LEND_USER"],
    "start_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

# Create the test run
new_test_run = rpc.TestRun.create(test_run_data)
print("New Test Run created:", new_test_run)

# Fetch the runner_id for the created test run
search_name = test_run_data["summary"]
runs = rpc.TestRun.filter({"summary": search_name})
for r in runs:
    runner_id = r["id"]

# Add all cases from the plan to the run
test_cases = rpc.TestCase.filter({"plan": tcms_maps.TEST_PLANS["LEND_LOGIN_BACKEND"]})
for case in test_cases:
    rpc.TestRun.add_case(runner_id, case["id"])

# ====================== Step 1: Send OTP ======================

def test_send_otp_first_time():
    data = {"phone_number": PHONE_NUMBER}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending OTP request

    set_exec_status("test_send_otp_first_time", response.status_code == 200)
    assert response.status_code == 200

# Test case for sending OTP again when it was already requested
def test_send_otp_second_time():
    data = {"phone_number": PHONE_NUMBER}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending OTP request again
    print(response.status_code)

    set_exec_status("test_send_otp_second_time", response.status_code == 200)
    assert response.status_code == 200  # Expecting a failure response

def test_send_otp_third_time():
    data = {"phone_number": PHONE_NUMBER}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending OTP request again
    print(response.status_code)

    ok = response.status_code == 400 and response.json()["error"] == "کد ورود قبلا ارسال شده است"
    set_exec_status("test_send_otp_third_time", ok)
    assert response.status_code == 400  # Expecting a failure response
    assert response.json()["error"] == "کد ورود قبلا ارسال شده است"  # Checking expected error message

# Test case for logging in with the correct OTP
def test_login_correct_otp():
    code = input("Enter OTP Code: ")  # Getting OTP code from user input
    data = {"phone_number": PHONE_NUMBER, "code": code}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending login request
    response_body = response.json()  # Extracting response data
    schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "pattern": "^[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_=]+\\.?[A-Za-z0-9-_.+/=]*$",
                    },
                    "refresh_token": {
                        "type": "string",
                        "pattern": "^[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_=]+\\.?[A-Za-z0-9-_.+/=]*$",
                    },
                },
                "required": ["access_token", "refresh_token"],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error"],
    }

    ok = response.status_code == 200 and schema_validator(response_body, schema) is None
    set_exec_status("test_login_correct_otp", ok)
    assert response.status_code == 200
    schema_validator(response_body, schema)  # Validating response schema
    update_token_in_constants(response_body["data"]["access_token"])  # Updating token in constants.py


# Test case for logging in with an incorrect OTP
def test_login_incorrect_otp():
    data = {"phone_number": PHONE_NUMBER, "code": "111111"}  # Providing incorrect OTP
    response = UserAPI().post_login(data)  # Sending login request

    set_exec_status("test_login_incorrect_otp", response.status_code == 401)
    assert response.status_code == 401  # Ensuring the login fails

# -------------------- After Test Run --------------------
rpc.TestRun.update(runner_id, {
    'stop_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
})
print(f"Test run with ID {runner_id} stopped and updated.")
