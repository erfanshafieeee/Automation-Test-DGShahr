from api_collections import LoanAPI, AssuranceAPI
from constants import BIRTH_DATE, NATIONAL_CODE , TCMS_URL , TCMS_USERNAME , TCMS_PASSWORD
import time
import pytest
from common_functions import schema_validator, upload_image
import datetime
from tcms_api import TCMS
import TCMS_tools.tcms_maps as tcms_maps

# TCMS setup
tcms_url = TCMS_URL
tcms_username = TCMS_USERNAME
tcms_password = TCMS_PASSWORD
rpc = TCMS(tcms_url, tcms_username, tcms_password).exec

loan_id = 0
credit_rank = ""

now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

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

def add_failure_note_to_tcms(test_case_summary: str, failure_reason: str):
    """Add a failure note to the test case in TCMS."""
    case_id = _get_case_id_in_run(runner_id, test_case_summary)
    
    note_data = {
        "note": failure_reason,
        "note_type": "failure"
    }
    
    rpc.TestCase.update(case_id, {"notes": [note_data]})
    print(f"[TCMS] Failure note added to Test Case '{test_case_summary}': {failure_reason}")

# -------------------- create Test Run & add cases --------------------
test_run_data = {
    "summary": f"test_lend_loan_flow_from_zero {now_str}",
    "plan": tcms_maps.TEST_PLANS["LEND_USER_BACKEND"],
    "build": tcms_maps.BUILDS_BY_PRODUCT[str(tcms_maps.PRODUCTS["LEND_USER"])]["unspecified"],
    "manager": tcms_maps.USERS["dgstack"],
    "product": tcms_maps.PRODUCTS["LEND_USER"],
    "start_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}
new_test_run = rpc.TestRun.create(test_run_data)
print("New Test Run created:", new_test_run)

search_name = test_run_data["summary"]
runs = rpc.TestRun.filter({"summary": search_name})
for r in runs:
    runner_id = r["id"]

# add all cases from the plan to the run
test_cases = rpc.TestCase.filter({"plan": tcms_maps.TEST_PLANS["LEND_USER_BACKEND"]})
for case in test_cases:
    rpc.TestRun.add_case(runner_id, case["id"])

# ====================== Step 1: Loan Request ======================

def test_get_primary_info_registration_personal():
    try:
        resp = LoanAPI().get_loan_request(0, "primary_info_registration__personal")
        set_exec_status("test_get_primary_info_registration_personal", resp.status_code == 200)
        assert resp.status_code == 200
    except AssertionError as e:
        add_failure_note_to_tcms("test_get_primary_info_registration_personal", str(e))
        raise e

def test_create_primary_info_registration_personal_befor_sabtAhval():
    global loan_id
    data = {"company": "other", "employment_status": "official", "shop": None}
    resp = LoanAPI().post_loan_request(0, "primary_info_registration__personal", data)
    set_exec_status("test_create_primary_info_registration_personal_befor_sabtAhval", resp.status_code == 400)
    assert resp.status_code == 400

def test_incorrect_nationalCode():
    data = {"national_code": "3730528262", "shamsi_birth_date": BIRTH_DATE}
    resp = LoanAPI().post_user_validation(data)
    ok = (resp.status_code == 406) and (resp.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد.")
    set_exec_status("test_incorrect_nationalCode", ok)
    assert resp.status_code == 406
    assert resp.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد."

def test_incorrect_nationalCode_and_birthDate():
    data = {"national_code": "3730528262", "shamsi_birth_date": "1381/10/10"}
    resp = LoanAPI().post_user_validation(data)
    ok = (resp.status_code == 406) and (resp.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد.")
    set_exec_status("test_incorrect_nationalCode_and_birthDate", ok)
    assert resp.status_code == 406
    assert resp.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد."

def test_incorrect_birthDate():
    data = {"national_code": NATIONAL_CODE, "shamsi_birth_date": "1381/10/10"}
    resp = LoanAPI().post_user_validation(data)
    ok = (resp.status_code == 400) and (
        resp.json()["error"] == "تاریخ تولد وارد شده با کد ملی تطابق ندارد و یا مشکلی پیش آمده است. لطفا در صورت صحت تاریخ تولد وارد شده، بعدا تلاش کنید."
    )
    set_exec_status("test_incorrect_birthDate", ok)
    assert resp.status_code == 400
    assert resp.json()["error"] == "تاریخ تولد وارد شده با کد ملی تطابق ندارد و یا مشکلی پیش آمده است. لطفا در صورت صحت تاریخ تولد وارد شده، بعدا تلاش کنید."

def test_correct_info():
    data = {"national_code": NATIONAL_CODE, "shamsi_birth_date": BIRTH_DATE}
    resp = LoanAPI().post_user_validation(data)
    set_exec_status("test_correct_info", resp.status_code == 200)
    assert resp.status_code == 200

def test_create_primary_info_registration_personal():
    global loan_id
    data = {"company": "other", "employment_status": "official", "shop": None}
    resp = LoanAPI().post_loan_request(0, "primary_info_registration__personal", data)
    body = resp.json()

    schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "loan_id": {"type": "integer"},
                    "national_code": {"type": "string"},
                    "shamsi_birth_date": {"type": "string", "pattern": "^[0-9]{4}/[0-9]{2}/[0-9]{2}$"},
                    "employment_status": {"type": "string", "enum": ["contractor", "official", "retired", "self_employed", "other"]},
                    "company": {"type": "string", "enum": ["armed_forces", "edu_department", "edu_deputy", "milad_tower", "ministry_of_energy", "shahr_bank", "shahrdari", "other"]},
                },
                "required": ["loan_id", "national_code", "shamsi_birth_date", "employment_status", "company"],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error"],
    }

    ok = (resp.status_code == 201) and schema_validator(body, schema) is None
    set_exec_status("test_create_primary_info_registration_personal", ok)

    assert resp.status_code == 201
    schema_validator(body, schema)
    loan_id = body["data"]["loan_id"]

def test_change_birthdate():
    data = {"national_code": NATIONAL_CODE, "shamsi_birth_date": "1380/01/01"}
    resp = LoanAPI().post_user_validation(data)
    ok = (resp.status_code == 400) and (resp.json()["error"] == "تاریخ تولد قابل ویرایش نمی‌باشد.")
    set_exec_status("test_change_birthdate", ok)
    assert resp.status_code == 400
    assert resp.json()["error"] == "تاریخ تولد قابل ویرایش نمی‌باشد."

def test_duplicate_loan_request():
    data = {
        "company": "other",
        "employment_status": "official",
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": BIRTH_DATE,
        "shop": None,
    }
    resp = LoanAPI().post_loan_request(0, "primary_info_registration__personal", data)
    ok = (resp.status_code == 400) and (
        resp.json()["error"]
        == "درخواست وام دیگری برای شما در حال بررسی است. لطفا تا تکمیل مراحل درخواست وام پیشین منتظر بمانید و یا درخواست وام پیشین را حذف کنید."
    )
    set_exec_status("test_duplicate_loan_request", ok)
    assert resp.status_code == 400
    assert resp.json()["error"] == "درخواست وام دیگری برای شما در حال بررسی است. لطفا تا تکمیل مراحل درخواست وام پیشین منتظر بمانید و یا درخواست وام پیشین را حذف کنید."

# ====================== Step 2: Credit Rank ======================

def test_credit_rank_data():
    global credit_rank

    schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "credit_rank": {"type": ["string", "null"], "enum": ["A", "B", "C", "D", "E", "0"]},
                    "has_no_bounced_check": {"type": ["boolean", "null"]},
                    "military_service_status": {"type": ["boolean", "null"]},
                    "employment_status": {"type": "string"},
                    "has_postponed_loans": {"type": ["boolean", "null"]},
                    "status": {"type": "string"},
                    "old": {"type": "boolean"},
                    "user_id": {"type": "string"},
                    "user_info": {
                        "type": "object",
                        "properties": {
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "birth_certificate_number": {"type": "string"},
                            "gender": {"type": "string", "enum": ["مرد", "زن"]},
                            "father_name": {"type": "string"},
                        },
                        "required": ["first_name", "last_name", "birth_certificate_number", "gender", "father_name"],
                    },
                    "credit_rank_link": {"type": ["string", "null"]},
                    "min_amount": {"type": ["integer", "null"]},
                    "max_amount": {"type": ["integer", "null"]},
                    "guarantees": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {"value": {"type": "integer"}, "title": {"type": "string"}, "deprecated": {"type": "boolean"}},
                            "required": ["value", "title", "deprecated"],
                        },
                    },
                    "credit_status": {"type": ["string", "null"]},
                },
                "required": [
                    "has_no_bounced_check",
                    "military_service_status",
                    "employment_status",
                    "has_postponed_loans",
                    "status",
                    "old",
                    "user_id",
                    "user_info",
                ],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
            "error_type": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error", "error_type"],
    }

    while True:
        resp = LoanAPI().get_loan_request(loan_id, "primary_info_registration__credit_rank")
        assert resp.status_code == 200
        body = resp.json()
        if body["data"]["credit_status"] is not None:
            ok = schema_validator(body, schema) is None
            set_exec_status("test_credit_rank_data", ok)
            break
        time.sleep(3)

def test_complete_credit_rank_step():
    resp = LoanAPI().post_loan_request(loan_id, "primary_info_registration__auth_otp", {})
    set_exec_status("test_complete_credit_rank_step", resp.status_code == 200)
    assert resp.status_code == 200

# ====================== Step 3: Loan Amount And Guarantee ======================

def test_get_loan_data():
    resp = LoanAPI().get_loan_request(loan_id, "loan_request")
    body = resp.json()
    schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "guarantees": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {"value": {"type": "number"}, "title": {"type": "string"}, "deprecated": {"type": "boolean"}},
                            "required": ["value", "title", "deprecated"],
                        },
                    }
                },
                "required": ["guarantees"],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error"],
    }
    ok = (resp.status_code == 200) and schema_validator(body, schema) is None
    set_exec_status("test_get_loan_data", ok)
    assert resp.status_code == 200
    schema_validator(body, schema)

def test_loan_config():
    resp = LoanAPI().get_loan_configs()
    expected = {
        "12": {"min_loan_amount": 100000000, "max_loan_amount": 3000000000, "wage": 9},
        "24": {"min_loan_amount": 100000000, "max_loan_amount": 3000000000, "wage": 15},
        "36": {"min_loan_amount": 510000000, "max_loan_amount": 3000000000, "wage": 15},
        "48": {"min_loan_amount": 810000000, "max_loan_amount": 3000000000, "wage": 15},
        "60": {"min_loan_amount": 1210000000, "max_loan_amount": 3000000000, "wage": 15},
    }
    ok = (resp.status_code == 200) and (resp.json() == expected)
    set_exec_status("test_loan_config", ok)
    assert resp.status_code == 200
    assert resp.json() == expected

def test_code_generator():
    params = {"loan_id": loan_id}
    resp = AssuranceAPI().get_code_generate(params)
    body = resp.json()
    schema = {
        "type": "object",
        "properties": {
            "data": {"type": "object", "properties": {"assurance_code": {"type": "integer"}}, "required": ["assurance_code"]},
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
            "error_type": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error", "error_type"],
    }
    ok = (resp.status_code == 200) and schema_validator(body, schema) is None
    set_exec_status("test_code_generator", ok)
    assert resp.status_code == 200
    schema_validator(body, schema)

def test_loan_data_correct_period():
    amount, period, guarantee = 600000000, 24, "MY_CHECK"
    data = {"amount": amount, "period": period, "guarantee": guarantee}
    resp = LoanAPI().post_loan_request(loan_id, "loan_request", data)
    body = resp.json()
    schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "const": amount},
                    "period": {"type": "number", "const": period},
                    "guarantee": {"type": "string", "const": guarantee},
                    "invoice": {"type": ["number", "null"]},
                    "payment": {"type": "number"},
                    "wage": {"type": "number"},
                    "credit": {"type": "number"},
                    "version": {"type": "number"},
                    "min_amount": {"type": "number"},
                    "max_amount": {"type": "number"},
                    "assurance_code": {"type": "string"},
                },
                "required": ["amount", "period", "guarantee", "payment", "wage", "credit", "version", "min_amount", "max_amount", "assurance_code"],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error"],
    }
    ok = (resp.status_code == 200) and schema_validator(body, schema) is None
    set_exec_status("test_loan_data_correct_period", ok)
    assert resp.status_code == 200
    schema_validator(body, schema)

def test_loan_data_incorrect_period():
    data = {"amount": 100000000, "period": 60, "guarantee": "MY_CHECK"}
    resp = LoanAPI().post_loan_request(loan_id, "loan_request", data)
    set_exec_status("test_loan_data_incorrect_period", resp.status_code == 400)
    assert resp.status_code == 400

# ====================== Step 4: Info Completion Identity ======================

file_path_identity = list()

@pytest.mark.parametrize("step", [("national_card_front"), ("national_card_back"), ("birth_certificate_page_1"), ("birth_certificate_page_2"), ("birth_certificate_page_3")])
def test_partial_upload_identity(step):
    global file_path_identity
    resp = upload_image("low_size.png", step, "png")
    ok1 = (resp.status_code == 200)

    if ok1:
        file_path_identity.append(resp.json()["data"]["file_path"])
        data = {step: resp.json()["data"]["file_path"]}
        resp2 = LoanAPI().patch_loan_request(loan_id, "info_completion__identity", data)
        ok2 = (resp2.status_code == 200)
        set_exec_status("test_partial_upload_identity", ok2)
        assert ok2
    else:
        set_exec_status("test_partial_upload_identity", False)
        assert False, "Upload failed"

def test_complete_identity_step():
    global file_path_identity
    data = {
        "national_card_front": file_path_identity[0],
        "national_card_back": file_path_identity[1],
        "birth_certificate_page_1": file_path_identity[2],
        "birth_certificate_page_2": file_path_identity[3],
        "birth_certificate_page_3": file_path_identity[4],
    }
    resp = LoanAPI().post_loan_request(loan_id, "info_completion__identity", data)
    set_exec_status("test_complete_identity_step", resp.status_code == 200)
    assert resp.status_code == 200

# ====================== Step 5: Info Completion Residence ======================

def test_get_residence_data():
    resp = LoanAPI().get_loan_request(loan_id, "info_completion__residence")
    set_exec_status("test_get_residence_data", resp.status_code == 200)
    assert resp.status_code == 200

file_path_residence = list()

def test_partial_upload_residence():
    global file_path_residence
    resp = upload_image("low_size.png", "residence_document", "png")
    ok1 = (resp.status_code == 200)

    if ok1:
        file_path_residence = resp.json()["data"]["file_path"]
        data = {"residence_document": resp.json()["data"]["file_path"]}
        resp2 = LoanAPI().patch_loan_request(loan_id, "info_completion__residence", data)
        ok2 = (resp2.status_code == 200)
        set_exec_status("test_partial_upload_residence", ok2)
        assert ok2
    else:
        set_exec_status("test_partial_upload_residence", False)
        assert False, "Upload failed"

def test_complete_residence_step():
    data = {
        "address": "کرج",
        "city_id": 229,
        "post_code": "3135783604",
        "residence_document": file_path_residence,
        "work_address": "کرج",
        "housing_status": "OWNER",
    }
    resp = LoanAPI().post_loan_request(loan_id, "info_completion__residence", data)
    set_exec_status("test_complete_residence_step", resp.status_code == 200)
    assert resp.status_code == 200

# ====================== Step 6: Info Completion Occupation ======================

def test_get_occupation_data():
    resp = LoanAPI().get_loan_request(loan_id, "info_completion__occupation")
    set_exec_status("test_get_occupation_data", resp.status_code == 200)
    assert resp.status_code == 200

file_path_occupation = list()

@pytest.mark.parametrize("step", [("work_reference_letter"), ("last_payment_receipt")])
def test_partial_upload_occupation(step):
    global file_path_occupation
    resp = upload_image("low_size.png", step, "png")
    ok1 = (resp.status_code == 200)

    if ok1:
        file_path_occupation.append(resp.json()["data"]["file_path"])
        set_exec_status("test_partial_upload_occupation", True)
        assert True
    else:
        set_exec_status("test_partial_upload_occupation", False)
        assert False, "Upload failed"

def test_complete_occupation_step():
    data = {
        "work_reference_letter": file_path_occupation[0],
        "last_payment_receipt": file_path_occupation[1],
        "average_income": "FIFTEEN_TO_TWENTY",
    }
    resp = LoanAPI().post_loan_request(loan_id, "info_completion__occupation", data)
    set_exec_status("test_complete_occupation_step", resp.status_code == 200)
    assert resp.status_code == 200

# ====================== Step 7: Info Completion Branch ======================

def test_get_branch_step_data():
    resp = LoanAPI().get_loan_request(loan_id, "info_completion__branch")
    set_exec_status("test_get_branch_step_data", resp.status_code == 200)
    assert resp.status_code == 200

def test_complete_branch_step():
    resp = LoanAPI().post_loan_request(loan_id, "info_completion__branch", {"branch_id": 7})
    set_exec_status("test_complete_branch_step", resp.status_code == 200)
    assert resp.status_code == 200

rpc.TestRun.update(runner_id, {
    'stop_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
})
