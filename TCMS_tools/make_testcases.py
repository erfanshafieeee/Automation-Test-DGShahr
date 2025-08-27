from tcms_api import TCMS
import tcms_maps

url = "https://kiwi.dgstack.ir/xml-rpc/"
username = "dgstack"
password = "jO8Rqmzy8l"

rpc = TCMS(url, username, password).exec

# List of test case names to create
TEST_CASE_NAMES = [
    "test_get_primary_info_registration_personal",
    "test_create_primary_info_registration_personal_befor_sabtAhval",
    "test_incorrect_nationalCode",
    "test_incorrect_nationalCode_and_birthDate",
    "test_incorrect_birthDate",
    "test_correct_info",
    "test_create_primary_info_registration_personal",
    "test_change_birthdate",
    "test_duplicate_loan_request",
    "test_credit_rank_data",
    "test_complete_credit_rank_step",
    "test_get_loan_data",
    "test_loan_config",
    "test_code_generator",
    "test_loan_data_correct_period",
    "test_loan_data_incorrect_period",
    "test_partial_upload_identity",
    "test_complete_identity_step",
    "test_get_residence_data",
    "test_partial_upload_residence",
    "test_complete_residence_step",
    "test_get_occupation_data",
    "test_partial_upload_occupation",
    "test_complete_occupation_step",
    "test_get_branch_step_data",
    "test_complete_branch_step",
    "test_validate_incorrect_code",
    "test_validate_correct_code",
    "test_complete_primary_info_registration_personal",
    "test_send_otp_first_time" , 
    "test_send_otp_second_time",
    "test_send_otp_third_time" ,
    "test_login_correct_otp" , 
    "test_login_incorrect_otp",
    "get_URL",
    "login",
    "loan_request_down_button",
    "continue_button",
    "Upload_identity_documents",
    "Residence_documents",
    "loan_request_top_button",
    "primary_info_page",
    "cross_button",
    "is_credit_approved",
    "credit_rank_page",
    "gurantee_page",
    "Upload_job_documents_page",
    "login_and_navigate",
    "identity_documents_page",
    "Residence_documents_page",
    "loan_info_last_page"
]

# Default values from tcms_maps
DEFAULTS = {
    "category": tcms_maps.CATEGORIES_BY_PRODUCT[str(tcms_maps.PRODUCTS["LEND_USER"])]["FRONTEND"],
    "priority": tcms_maps.PRIORITIES["Critical"],
    "author": tcms_maps.USERS["dgstack"],
    "case_status": tcms_maps.TEST_CASE_STATUSES["PROPOSED"],
    "product": tcms_maps.PRODUCTS["LEND_USER"],
}

# Create test cases
for name in TEST_CASE_NAMES:
    case_data = {
        "summary": name,
        "category": DEFAULTS["category"],
        "priority": DEFAULTS["priority"],
        "author": DEFAULTS["author"],
        "case_status": DEFAULTS["case_status"],
        "product": DEFAULTS["product"],
        "is_automated": True,
    }

    try:
        new_case = rpc.TestCase.create(case_data)
        print(f"✅ Created: {new_case['id']} → {new_case['summary']}")
    except Exception as e:
        print(f"⚠️ Could not create test case '{name}': {e}")
