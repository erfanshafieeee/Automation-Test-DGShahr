from api_collections import LoanAPI, AssuranceAPI
from constants import BIRTH_DATE, NATIONAL_CODE
import time
import pytest
from common_functions import schema_validator, upload_image

loan_id = 0
credit_rank = ""

####################### Step 1: Loan Request #######################

# Test retrieving primary personal registration information
# Expects a 200 status code if the request is successful

def test_get_primary_info_registration_personal():
    response = LoanAPI().get_loan_request(0, "primary_info_registration__personal")
    assert response.status_code == 200

# Test creating a loan request before national registry validation
# Expects a 400 status code because the request should not be allowed before registry validation

def test_create_primary_info_registration_personal_befor_sabtAhval():
    global loan_id
    data = {
        "company": "other",
        "employment_status": "official",
        "shop": None,
    }
    response = LoanAPI().post_loan_request(0, "primary_info_registration__personal", data)
    assert response.status_code == 400

# Test validation with an incorrect national code
# Expects a 406 status code with an error message indicating the mismatch

def test_incorrect_nationalCode():
    data = {
        "national_code": "3730528262",
        "shamsi_birth_date": BIRTH_DATE,
    }
    response = LoanAPI().post_user_validation(data)
    assert response.status_code == 406
    assert response.json()["error"] == "شماره موبایل شما متعلق به کد ملی وارد شده نمی باشد."

# Test validation with incorrect national code and birth date
# Expects a 406 status code with an error message indicating the mismatch

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

# Test creating a primary personal registration loan request
# Expects a 201 status code for successful creation and schema validation

def test_create_primary_info_registration_personal():
    global loan_id
    data = {
        "company": "other",
        "employment_status": "official",
        "shop": None,
    }
    response = LoanAPI().post_loan_request(0, "primary_info_registration__personal", data)
    assert response.status_code == 201

    response_body = response.json()

    # Schema validation to ensure correct data structure
    schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "loan_id": {"type": "integer"},
                    "national_code": {"type": "string"},
                    "shamsi_birth_date": {
                        "type": "string",
                        "pattern": "^[0-9]{4}/[0-9]{2}/[0-9]{2}$",
                    },
                    "employment_status": {
                        "type": "string",
                        "enum": [
                            "contractor",
                            "official",
                            "retired",
                            "self_employed",
                            "other",
                        ],
                    },
                    "company": {
                        "type": "string",
                        "enum": [
                            "armed_forces",
                            "edu_department",
                            "edu_deputy",
                            "milad_tower",
                            "ministry_of_energy",
                            "shahr_bank",
                            "shahrdari",
                            "other",
                        ],
                    },
                },
                "required": [
                    "loan_id",
                    "national_code",
                    "shamsi_birth_date",
                    "employment_status",
                    "company",
                ],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error"],
    }
    schema_validator(response_body, schema)

    loan_id = response_body["data"]["loan_id"]

# Test changing birth date after initial registration
# Expects a 400 status code indicating that birth date modification is not allowed

def test_change_birthdate():
    data = {
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": "1380/01/01",
    }
    response = LoanAPI().post_user_validation(data)
    assert response.status_code == 400
    assert response.json()["error"] == "تاریخ تولد قابل ویرایش نمی‌باشد."

# Test duplicate loan request submission
# Expects a 400 status code indicating that a previous loan request is still in progress

def test_duplicate_loan_request():
    data = {
        "company": "other",
        "employment_status": "official",
        "national_code": NATIONAL_CODE,
        "shamsi_birth_date": BIRTH_DATE,
        "shop": None,
    }
    response = LoanAPI().post_loan_request(0, "primary_info_registration__personal", data)
    assert response.status_code == 400
    assert response.json()["error"] == "درخواست وام دیگری برای شما در حال بررسی است. لطفا تا تکمیل مراحل درخواست وام پیشین منتظر بمانید و یا درخواست وام پیشین را حذف کنید."

####################### Step 2: Credit Rank #######################

# Test retrieving credit rank data and validating schema
# Waits until the credit status is available before validating

def test_credit_rank_data():
    global credit_rank

    schema = {
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "properties": {
                "credit_rank": {
                    "type": ["string", "null"],
                    "enum": ["A", "B", "C", "D", "E", "0",]
                },
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
                        "father_name": {"type": "string"}
                    },
                    "required": [
                        "first_name",
                        "last_name",
                        "birth_certificate_number",
                        "gender",
                        "father_name"
                    ]
                },
                "credit_rank_link": {"type": ["string", "null"]},
                "min_amount": {"type": ["integer", "null"]},
                "max_amount": {"type": ["integer", "null"]},
                "guarantees": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "integer"},
                            "title": {"type": "string"},
                            "deprecated": {"type": "boolean"}
                        },
                        "required": ["value", "title", "deprecated"]
                    }
                },
                "credit_status": {"type": ["string", "null"]}
            },
            "required": [
                "has_no_bounced_check",
                "military_service_status",
                "employment_status",
                "has_postponed_loans",
                "status",
                "old",
                "user_id",
                "user_info"
            ]
        },
        "message": {"type": ["string", "null"]},
        "error": {"type": ["string", "null"]},
        "error_type": {"type": ["string", "null"]}
    },
    "required": ["data", "message", "error", "error_type"]
}

    while True:
        response = LoanAPI().get_loan_request(loan_id, "primary_info_registration__credit_rank")
        assert response.status_code == 200

        response_body = response.json()
        if response_body["data"]["credit_status"] is not None:
            schema_validator(response_body, schema)  # Validate the response schema
            break
        
        time.sleep(3)  # Wait before retrying
    
    # credit_rank = response_body["data"]["credit_status"]

# Test completing the credit rank step
# Sends an empty data payload to move to the next step
# Expects a 200 status code indicating success

def test_complete_credit_rank_step():
    data = {}
    response = LoanAPI().post_loan_request(loan_id, "primary_info_registration__auth_otp", data)
    assert response.status_code == 200

####################### Step 3: Loan Amount And Guarantee #######################

# Test retrieving loan data and validating schema
# Ensures the guarantees field is correctly structured

def test_get_loan_data():
    response = LoanAPI().get_loan_request(loan_id, "loan_request")
    assert response.status_code == 200

    response_body = response.json()
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
                            "properties": {
                                "value": {"type": "number"},
                                "title": {"type": "string"},
                                "deprecated": {"type": "boolean"},
                            },
                            "required": ["value", "title", "deprecated"],
                        },
                    },
                },
                "required": ["guarantees"],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error"],
    }
    schema_validator(response_body, schema)

# Test retrieving loan configuration settings
# Ensures the response matches the predefined schema

def test_loan_config():
    response = LoanAPI().get_loan_configs()
    assert response.status_code == 200

    schema = {
        "12": {"min_loan_amount": 100000000, "max_loan_amount": 3000000000, "wage": 9},
        "24": {"min_loan_amount": 100000000, "max_loan_amount": 3000000000, "wage": 15},
        "36": {"min_loan_amount": 510000000, "max_loan_amount": 3000000000, "wage": 15},
        "48": {"min_loan_amount": 810000000, "max_loan_amount": 3000000000, "wage": 15},
        "60": {"min_loan_amount": 1210000000, "max_loan_amount": 3000000000, "wage": 15},
    }
    assert response.json() == schema

# Test generating an assurance code
# Ensures the response contains a valid assurance_code

def test_code_generator():
    params = {"loan_id": loan_id}
    response = AssuranceAPI().get_code_generate(params)
    assert response.status_code == 200

    response_body = response.json()
    schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "assurance_code": {"type": "integer"}
                },
                "required": ["assurance_code"]
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
            "error_type": {"type": ["string", "null"]}
        },
        "required": ["data", "message", "error", "error_type"]
    }
    schema_validator(response_body, schema)

# Test loan data submission with a correct period
# Ensures the loan request is accepted and validated

def test_loan_data_correct_period():
    amount = 600000000
    period = 24
    guarantee = "MY_CHECK"
    
    data = {"amount": amount, "period": period, "guarantee": guarantee}
    
    response = LoanAPI().post_loan_request(loan_id, "loan_request", data)
    assert response.status_code == 200

    response_body = response.json()
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
                "required": [
                    "amount",
                    "period",
                    "guarantee",
                    "payment",
                    "wage",
                    "credit",
                    "version",
                    "min_amount",
                    "max_amount",
                    "assurance_code",
                ],
            },
            "message": {"type": ["string", "null"]},
            "error": {"type": ["string", "null"]},
        },
        "required": ["data", "message", "error"],
    }
    schema_validator(response_body, schema)

# Test loan data submission with an incorrect period
# Ensures the loan request is rejected with a 400 error

def test_loan_data_incorrect_period():
    data = {
        "amount":100000000,
        "period":60,
        "guarantee":"MY_CHECK"
    }
    response = LoanAPI().post_loan_request(loan_id, "loan_request", data)
    assert response.status_code == 400

####################### Step 4: Info Completion Identity #######################

# List to store file paths for uploaded identity documents
file_path_identity = list()

# Test uploading identity documents one by one
# Uses parameterized testing for different document types
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
    response = LoanAPI().patch_loan_request(loan_id, "info_completion__identity", data)
    assert response.status_code == 200

# Test completing the identity step
# Submits all uploaded identity documents in a final request

def test_complete_identity_step():
    global file_path_identity
    
    data = {
        "national_card_front": file_path_identity[0],
        "national_card_back": file_path_identity[1],
        "birth_certificate_page_1": file_path_identity[2],
        "birth_certificate_page_2": file_path_identity[3],
        "birth_certificate_page_3": file_path_identity[4],
    }
    response = LoanAPI().post_loan_request(loan_id, "info_completion__identity", data)
    assert response.status_code == 200

####################### Step 5: Info Completion Residence #######################

# Test retrieving residence information
# Ensures the residence data is accessible

def test_get_residence_data():
    response = LoanAPI().get_loan_request(loan_id, "info_completion__residence")
    assert response.status_code == 200

# List to store file path for uploaded residence document
file_path_residence = list()

# Test uploading residence document
# Ensures the document upload process is successful

def test_partial_upload_residence():
    global file_path_residence

    response = upload_image("low_size.png", "residence_document", "png")
    assert response.status_code == 200
    file_path_residence = response.json()["data"]["file_path"]
    data = {"residence_document": response.json()["data"]["file_path"]}
    response = LoanAPI().patch_loan_request(loan_id, "info_completion__residence", data)
    assert response.status_code == 200

# Test completing the residence step
# Submits all residence information along with the uploaded document

def test_complete_residence_step():
    data = {
        "address":"کرج",
        "city_id":229,
        "post_code":"3135783604",
        "residence_document": file_path_residence,
        "work_address":"کرج",
        "housing_status":"OWNER"
    }
    response = LoanAPI().post_loan_request(loan_id, "info_completion__residence", data)
    assert response.status_code == 200

####################### Step 6: Info Completion Occupation #######################

# Test retrieving occupation data
# Ensures the occupation information is accessible

def test_get_occupation_data():
    response = LoanAPI().get_loan_request(loan_id, "info_completion__occupation")
    assert response.status_code == 200

# List to store file paths for uploaded occupation-related documents
file_path_occupation = list()

# Test uploading occupation-related documents one by one
# Uses parameterized testing for different document types
@pytest.mark.parametrize("step", [
    ("work_reference_letter"),
    ("last_payment_receipt"),
])
def test_partial_upload_occupation(step):
    global file_path_occupation

    response = upload_image("low_size.png", step, "png")
    assert response.status_code == 200
    file_path_occupation.append(response.json()["data"]["file_path"])

# Test completing the occupation step
# Submits all uploaded occupation documents along with income details

def test_complete_occupation_step():
    data = {
        "work_reference_letter": file_path_occupation[0],
        "last_payment_receipt": file_path_occupation[1],
        "average_income": "FIFTEEN_TO_TWENTY",
    }
    response = LoanAPI().post_loan_request(loan_id, "info_completion__occupation", data)
    assert response.status_code == 200

####################### Step 7: Info Completion Branch #######################

# Test retrieving branch step data
# Ensures the branch information is accessible

def test_get_branch_step_data():
    response = LoanAPI().get_loan_request(loan_id, "info_completion__branch")
    assert response.status_code == 200

# Test completing the branch selection step
# Submits the selected branch ID for loan processing

def test_complete_branch_step():
    data = {"branch_id": 7}
    response = LoanAPI().post_loan_request(loan_id, "info_completion__branch", data)
    assert response.status_code == 200