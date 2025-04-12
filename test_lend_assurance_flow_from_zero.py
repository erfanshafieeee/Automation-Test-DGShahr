from api_collections import AssuranceAPI ,LoanAPI
from constants import BIRTH_DATE, NATIONAL_CODE, ASSURANCE_CODE
import time
import pytest
from common_functions import upload_image
from functions import set_pro_user


assurance_id = 0

####################### Step 1: Validate Assurance Code #######################
def test_validate_incorrect_code():
    data = {}
    params = {"assurance_code": "TTTTTT"}
    response = AssuranceAPI().post_assurances_validity(data, params)
    assert response.status_code == 403


def test_validate_correct_code():
    data = {}
    params = {"assurance_code": ASSURANCE_CODE}
    response = AssuranceAPI().post_assurances_validity(data, params)
    assert response.status_code == 200


####################### Step 2: Assurance Requests #######################
def test_get_primary_info_registration_personal():
    response = AssuranceAPI().get_assurance_request(0, "primary_info_registration__personal")
    assert response.status_code == 200

def test_incorrect_nationalCode():
    data = {
        "national_code": "2720695588",
        "shamsi_birth_date": BIRTH_DATE
    }
    response = LoanAPI().post_user_validation(data)
    #response = AssuranceAPI().post_assurance_request(0, "primary_info_registration__personal", data)
    assert response.status_code == 406
    assert response.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد."

def test_incorrect_nationalCode_and_birthDate():
    data = {
        "national_code": "3730528262",
        "shamsi_birth_date": "1381/10/10",
    }
    response = LoanAPI().post_user_validation(data)
    assert response.status_code == 406
    assert response.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد."

# Test validation with an incorrect birth date
# Expects a 400 status code with an error message about the mismatch

def test_incorrect_birthDate():
    data = {
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": "1381/10/10",
    }
    response = LoanAPI().post_user_validation(data)
    assert response.status_code == 400
    assert response.json()["error"] == "تاریخ تولد وارد شده با کد ملی تطابق ندارد و یا مشکلی پیش آمده است. لطفا در صورت صحت تاریخ تولد وارد شده، بعدا تلاش کنید."

# Test validation with correct national code and birth date
# Expects a 200 status code for successful validation

def test_correct_info():
    data = {
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": BIRTH_DATE,
    }
    response = LoanAPI().post_user_validation(data)
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
    print(response.json())
    assert response.status_code == 201
    assurance_id = response.json()["data"]["assurance_id"]

def test_change_birthdate():
    # data = {
    #     "company": "other",
    #     "employment_status": "official",
    #     "national_code": NATIONAL_CODE,
    #     "shamsi_birth_date": "1390/01/01",
    #     "assurance_code": ASSURANCE_CODE,
    # }
    data = {
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": "1390/01/01"
    }
    response = LoanAPI().post_user_validation(data)
    #response = AssuranceAPI().patch_assurance_request(assurance_id, "primary_info_registration__personal", data)
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
    assert response.status_code == 400
    assert response.json()["error"] == "درخواست ضمانت دیگری برای شما در حال بررسی است. لطفا تا تکمیل مراحل درخواست ضمانت پیشین منتظر بمانید و یا درخواست ضمانت پیشین را حذف کنید."


####################### Step 3: Credit Rank #######################
def test_credit_rank_data():
    while True:
        response = AssuranceAPI().get_assurance_request(assurance_id, "primary_info_registration__credit_rank")
        assert response.status_code == 200
        if response.json()["data"]["credit_status"] is not None:
            if response.json()["data"]["credit_status"]=="not_allowed":
                set_pro_user()
            else:
                break
        time.sleep(3)
    
    

def test_complete_credit_rank_step():
    data = {}
    response = AssuranceAPI().post_assurance_request(assurance_id, "assurance_request", data)
    assert response.status_code == 200


####################### Step 4: Info Completion Identity #######################
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
    response = AssuranceAPI().patch_assurance_request(assurance_id, "info_completion__identity", data)
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
    assert response.status_code == 200


####################### Step 5: Info Completion Residence #######################
def test_get_residence_data():
    response = AssuranceAPI().get_assurance_request(assurance_id, "info_completion__residence")
    assert response.status_code == 200

file_path_residence = list()

def test_partial_upload_residence():
    global file_path_residence

    response = upload_image("low_size.png", "residence_document", "png")
    assert response.status_code == 200
    file_path_residence = response.json()["data"]["file_path"]
    data = {"residence_document": response.json()["data"]["file_path"]}
    response = AssuranceAPI().patch_assurance_request(assurance_id, "info_completion__residence", data)
    assert response.status_code == 200

def test_complete_residence_step():
    data = {
        "address":"کرج",
        "city_id":229,
        "post_code":"3135783604",
        "residence_document": file_path_residence,
        "work_address":"کرج",
        "housing_status":"OWNER"
    }
    response = AssuranceAPI().post_assurance_request(assurance_id, "info_completion__residence", data)
    assert response.status_code == 200


####################### Step 6: Info Completion Occupation #######################
def test_get_occupation_data():
    response = AssuranceAPI().get_assurance_request(assurance_id, "info_completion__occupation")
    assert response.status_code == 200

file_path_occupation = list()

@pytest.mark.parametrize("step", [
    ("work_reference_letter"),
    ("last_payment_receipt"),
])
def test_partial_upload_occupation(step):
    global file_path_occupation

    response = upload_image("low_size.png", step, "png")
    assert response.status_code == 200
    file_path_occupation.append(response.json()["data"]["file_path"])

def test_complete_occupation_step():
    data = {
        "work_reference_letter": file_path_occupation[0],
        "last_payment_receipt": file_path_occupation[1],
        "average_income": "FIFTEEN_TO_TWENTY",
    }
    response = AssuranceAPI().post_assurance_request(assurance_id, "info_completion__occupation", data)
    assert response.status_code == 200
