from api_collections import AssuranceAPI, LoanAPI
from constants import BIRTH_DATE, NATIONAL_CODE, ASSURANCE_CODE
import time
import pytest
from common_functions import upload_image
from functions import set_pro_user
from tcms_api import TCMS
import TCMS_tools.tcms_maps as tcms_maps
import datetime

# TCMS setup
url = "https://kiwi.dgstack.ir/xml-rpc/"
username = "dgstack"
password = "jO8Rqmzy8l"
rpc = TCMS(url, username, password).exec

assurance_id = 0

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
    "summary": f"test_lend_assurance_flow_from_zero {now_str}",
    "plan": tcms_maps.TEST_PLANS["LEND_USER_ASSURANCE_BACKEND"],
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

# Add all cases from the plan to the run
test_cases = rpc.TestCase.filter({"plan": tcms_maps.TEST_PLANS["LEND_USER_ASSURANCE_BACKEND"]})
for case in test_cases:
    rpc.TestRun.add_case(runner_id, case["id"])

# ====================== Step 1: Validate Assurance Code ======================
def test_validate_incorrect_code():
    data = {}
    params = {"assurance_code": "TTTTTT"}
    response = AssuranceAPI().post_assurances_validity(data, params)
    set_exec_status("test_validate_incorrect_code", response.status_code == 403)
    assert response.status_code == 403


def test_validate_correct_code():
    data = {}
    params = {"assurance_code": ASSURANCE_CODE}
    response = AssuranceAPI().post_assurances_validity(data, params)
    set_exec_status("test_validate_correct_code", response.status_code == 200)
    assert response.status_code == 200


# ====================== Step 2: Assurance Requests ======================
def test_get_primary_info_registration_personal():
    response = AssuranceAPI().get_assurance_request(0, "primary_info_registration__personal")
    set_exec_status("test_get_primary_info_registration_personal", response.status_code == 200)
    assert response.status_code == 200


def test_incorrect_nationalCode():
    data = {
        "national_code": "2720695588",
        "shamsi_birth_date": BIRTH_DATE
    }
    response = LoanAPI().post_user_validation(data)
    set_exec_status("test_incorrect_nationalCode", response.status_code == 406)
    assert response.status_code == 406
    assert response.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد."


def test_incorrect_nationalCode_and_birthDate():
    data = {
        "national_code": "3730528262",
        "shamsi_birth_date": "1381/10/10",
    }
    response = LoanAPI().post_user_validation(data)
    set_exec_status("test_incorrect_nationalCode_and_birthDate", response.status_code == 406)
    assert response.status_code == 406
    assert response.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد."


def test_incorrect_birthDate():
    data = {
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": "1381/10/10",
    }
    response = LoanAPI().post_user_validation(data)
    set_exec_status("test_incorrect_birthDate", response.status_code == 400)
    assert response.status_code == 400
    assert response.json()["error"] == "تاریخ تولد وارد شده با کد ملی تطابق ندارد و یا مشکلی پیش آمده است. لطفا در صورت صحت تاریخ تولد وارد شده، بعدا تلاش کنید."


def test_correct_info():
    data = {
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": BIRTH_DATE,
    }
    response = LoanAPI().post_user_validation(data)
    set_exec_status("test_correct_info", response.status_code == 200)
    assert response.status_code == 200


def test_complete_primary_info_registration_personal():
    global assurance_id
    data = {
        "company": "other",
        "employment_status": "official",
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": BIRTH_DATE,
        "assurance_code": ASSURANCE_CODE,
    }
    response = AssuranceAPI().post_assurance_request(0, "primary_info_registration__personal", data)
    set_exec_status("test_complete_primary_info_registration_personal", response.status_code == 201)
    assert response.status_code == 201
    assurance_id = response.json()["data"]["assurance_id"]


def test_change_birthdate():
    data = {
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": "1390/01/01"
    }
    response = LoanAPI().post_user_validation(data)
    set_exec_status("test_change_birthdate", response.status_code == 400)
    assert response.status_code == 400
    assert response.json()["error"] == "تاریخ تولد قابل ویرایش نمی‌باشد."


def test_duplicate_loan_request():
    data = {
        "company": "other",
        "employment_status": "official",
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": BIRTH_DATE,
        "shop": None,
    }
    response = AssuranceAPI().post_assurance_request(0, "primary_info_registration__personal", data)
    set_exec_status("test_duplicate_loan_request", response.status_code == 400)
    assert response.status_code == 400
    assert response.json()["error"] == "درخواست ضمانت دیگری برای شما در حال بررسی است. لطفا تا تکمیل مراحل درخواست ضمانت پیشین منتظر بمانید و یا درخواست ضمانت پیشین را حذف کنید."


# ====================== Step 3: Credit Rank ======================
def test_credit_rank_data():
    while True:
        response = AssuranceAPI().get_assurance_request(assurance_id, "primary_info_registration__credit_rank")
        set_exec_status("test_credit_rank_data", response.status_code == 200)
        assert response.status_code == 200
        if response.json()["data"]["credit_status"] is not None:
            if response.json()["data"]["credit_status"] == "not_allowed":
                set_pro_user()
            else:
                break
        time.sleep(3)


def test_complete_credit_rank_step():
    data = {}
    response = AssuranceAPI().post_assurance_request(assurance_id, "assurance_request", data)
    set_exec_status("test_complete_credit_rank_step", response.status_code == 200)
    assert response.status_code == 200


# ====================== Step 4: Info Completion Identity ======================
file_path_identity = list()

@pytest.mark.parametrize("step", [
    ("national_card_front"),
    ("national_card_back"),
    ("birth_certificate_page_1"),
    ("birth_certificate_page_2"),
    ("birth_certificate_page_3"),
])
def test_partial_upload_identity(step):
    global file_path_identity

    response = upload_image("low_size.png", step, "png")
    assert response.status_code == 200
    file_path_identity.append(response.json()["data"]["file_path"])
    data = {step: response.json()["data"]["file_path"]}
    resp = AssuranceAPI().patch_assurance_request(assurance_id, "info_completion__identity", data)
    ok = (response.status_code == 200) and (resp.status_code == 200)
    set_exec_status("test_partial_upload_identity" , ok)
    assert response.status_code == 200

def test_complete_identity_step():
    global file_path_identity
    
    data = {
        "national_card_front": file_path_identity[0],
        "national_card_back": file_path_identity[1],
        "birth_certificate_page_1": file_path_identity[2],
        "birth_certificate_page_2": file_path_identity[3],
        "birth_certificate_page_3": file_path_identity[4],
    }
    response = AssuranceAPI().post_assurance_request(assurance_id, "info_completion__identity", data)
    set_exec_status("test_complete_identity_step", response.status_code == 200)
    assert response.status_code == 200


# ====================== Step 5: Info Completion Residence ======================
def test_get_residence_data():
    response = AssuranceAPI().get_assurance_request(assurance_id, "info_completion__residence")
    set_exec_status("test_get_residence_data", response.status_code == 200)
    assert response.status_code == 200

file_path_residence = list()

def test_partial_upload_residence():
    global file_path_residence

    response = upload_image("low_size.png", "residence_document", "png")
    set_exec_status("test_partial_upload_residence", response.status_code == 200)
    assert response.status_code == 200
    file_path_residence = response.json()["data"]["file_path"]
    data = {"residence_document": response.json()["data"]["file_path"]}
    response = AssuranceAPI().patch_assurance_request(assurance_id, "info_completion__residence", data)
    assert response.status_code == 200

def test_complete_residence_step():
    data = {
        "address": "کرج",
        "city_id": 229,
        "post_code": "3135783604",
        "residence_document": file_path_residence,
        "work_address": "کرج",
        "housing_status": "OWNER"
    }
    response = AssuranceAPI().post_assurance_request(assurance_id, "info_completion__residence", data)
    set_exec_status("test_complete_residence_step", response.status_code == 200)
    assert response.status_code == 200


# ====================== Step 6: Info Completion Occupation ======================
def test_get_occupation_data():
    response = AssuranceAPI().get_assurance_request(assurance_id, "info_completion__occupation")
    set_exec_status("test_get_occupation_data", response.status_code == 200)
    assert response.status_code == 200

file_path_occupation = list()

@pytest.mark.parametrize("step", [
    ("work_reference_letter"),
    ("last_payment_receipt"),
])
def test_partial_upload_occupation(step):
    global file_path_occupation

    response = upload_image("low_size.png", step, "png")
    set_exec_status("test_partial_upload_occupation",response.status_code == 200 )
    assert response.status_code == 200
    file_path_occupation.append(response.json()["data"]["file_path"])

def test_complete_occupation_step():
    data = {
        "work_reference_letter": file_path_occupation[0],
        "last_payment_receipt": file_path_occupation[1],
        "average_income": "FIFTEEN_TO_TWENTY",
    }
    response = AssuranceAPI().post_assurance_request(assurance_id, "info_completion__occupation", data)
    set_exec_status("test_complete_occupation_step", response.status_code == 200)
    assert response.status_code == 200


# ====================== Finish and update TCMS ======================
rpc.TestRun.update(
    runner_id,
    {
        "stop_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
)
