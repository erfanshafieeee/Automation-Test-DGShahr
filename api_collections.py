# Import required libraries
import requests
from constants import SERVER, AUTH_TOKEN

# Base API client class that handles common HTTP operations
class BaseAPIClient:
    def __init__(self):
        self.base_url = SERVER
        self.session = requests.Session()
        self.session.headers.update({'Authorization': AUTH_TOKEN})
    
    # HTTP GET request
    def get(self, endpoint, params=None):
        return self.session.get(f"{self.base_url}{endpoint}", params=params)

    # HTTP POST request
    def post(self, endpoint, data=None, json=None, files=None, params=None):
        return self.session.post(f"{self.base_url}{endpoint}", data=data, json=json, files=files, params=params)

    # HTTP PUT request
    def put(self, endpoint, data=None):
        return self.session.put(f"{self.base_url}{endpoint}", data=data)

    # HTTP PATCH request
    def patch(self, endpoint, data=None):
        return self.session.patch(f"{self.base_url}{endpoint}", data=data)

    # HTTP DELETE request
    def delete(self, endpoint):
        return self.session.delete(f"{self.base_url}{endpoint}")


# API client for assurance related operations
class AssuranceAPI(BaseAPIClient):
    def get_assurance(self):
        return self.get("/assurance/")
    
    def delete_assurance(self, assurance_id):
        return self.delete(f"/assurance/{assurance_id}/")
    
    def get_assurance_request(self, assurance_id, step):
        return self.get(f"/assurance/request/{assurance_id}/{step}/")
    
    def post_assurance_request(self, assurance_id, step, data):
        return self.post(f"/assurance/request/{assurance_id}/{step}/", json=data)
    
    def patch_assurance_request(self, assurance_id, step, data):
        return self.patch(f"/assurance/request/{assurance_id}/{step}/", data=data)

    def get_code_generate(self, data):
        return self.get("/assurances/code_generate/", params=data)
    
    def delete_assurances(self):
        return self.delete("/assurances/delete_assurance/")
    
    def get_status(self):
        return self.get("/assurances/status/")
    
    def post_assurances_validity(self, data, params):
        return self.post("/assurances/validity/", json=data, params=params)

# API client for branch related operations
class BranchAPI(BaseAPIClient):
    def get_branches(self):
        return self.get("/branch/branches/")
    
    def update_branch(self, id, data):
        return self.put(f"/branch/branches/{id}/", data=data)
    
    def patch_branch(self, id, data):
        return self.patch(f"/branch/branches/{id}/", data=data)

# API client for document related operations
class DocumentAPI(BaseAPIClient):
    def get_forms(self):
        return self.get("/document/get_forms/")

# API client for file admin operations
class FileAdminAPI(BaseAPIClient):
    def upload(self, files):
        return self.post("/file-admin/upload/", files=files)

# API client for file operations
class FileAPI(BaseAPIClient):
    def get_link(self):
        return self.get("/file/get_link/")
    
    def upload(self, files):
        return self.post("/file/upload/", files=files)

# API client for address related operations
class AddressAPI(BaseAPIClient):
    def get_address_by_postal_code(self, data):
        return self.post("/get_address_by_postal_code/", json=data)

# API client for loan related operations
class LoanAPI(BaseAPIClient):
    def get_loans(self):
        return self.get("/loan/")

    def get_admin_message(self):
        return self.get("/loan/admin_message/")

    def post_admin_message(self, data):
        return self.post("/loan/admin_message/", json=data)

    def patch_admin_profile(self, data):
        return self.patch("/loan/admin_profile/", data=data)

    def get_admin_users(self):
        return self.get("/loan/admin_users/")

    def post_admin_users(self, data):
        return self.post("/loan/admin_users/", json=data)

    def get_admin_user(self, id):
        return self.get(f"/loan/admin_users/{id}/")

    def put_admin_user(self, id, data):
        return self.put(f"/loan/admin_users/{id}/", data=data)

    def patch_admin_user(self, id, data):
        return self.patch(f"/loan/admin_users/{id}/", data=data)

    def delete_admin_user(self, id):
        return self.delete(f"/loan/admin_users/{id}/")

    def get_assurance(self, assurance_id):
        return self.get(f"/loan/assurance/{assurance_id}")

    def post_assurance(self, assurance_id, data):
        return self.post(f"/loan/assurance/{assurance_id}", json=data)

    def patch_assurance(self, assurance_id, data):
        return self.patch(f"/loan/assurance/{assurance_id}", data=data)

    def delete_assurance(self, assurance_id):
        return self.delete(f"/loan/assurance/{assurance_id}")

    def get_assurance_admin_message(self):
        return self.get("/loan/assurance/admin_message/")

    def post_assurance_admin_message(self, data):
        return self.post("/loan/assurance/admin_message/", json=data)

    def get_branch_management(self):
        return self.get("/loan/branch_management/")

    def post_branch_management(self, data):
        return self.post("/loan/branch_management/", json=data)

    def get_branch_management_id(self, id):
        return self.get(f"/loan/branch_management/{id}/")

    def put_branch_management(self, id, data):
        return self.put(f"/loan/branch_management/{id}/", data=data)

    def patch_branch_management(self, id, data):
        return self.patch(f"/loan/branch_management/{id}/", data=data)

    def delete_branch_management(self, id):
        return self.delete(f"/loan/branch_management/{id}/")

    def get_loan_configs(self):
        return self.get("/loan/configs/")

    def get_detail_assurance(self):
        return self.get("/loan/detail_assurance/")

    def post_detail_assurance(self, data):
        return self.post("/loan/detail_assurance/", json=data)

    def get_detail_assurance_id(self, id):
        return self.get(f"/loan/detail_assurance/{id}/")

    def put_detail_assurance(self, id, data):
        return self.put(f"/loan/detail_assurance/{id}/", data=data)

    def patch_detail_assurance(self, id, data):
        return self.patch(f"/loan/detail_assurance/{id}/", data=data)

    def delete_detail_assurance(self, id):
        return self.delete(f"/loan/detail_assurance/{id}/")

    def get_detail_loan(self):
        return self.get("/loan/detail_loan/")

    def post_detail_loan(self, data):
        return self.post("/loan/detail_loan/", json=data)

    def get_detail_loan_id(self, id):
        return self.get(f"/loan/detail_loan/{id}/")

    def put_detail_loan(self, id, data):
        return self.put(f"/loan/detail_loan/{id}/", data=data)

    def patch_detail_loan(self, id, data):
        return self.patch(f"/loan/detail_loan/{id}/", data=data)

    def delete_detail_loan(self, id):
        return self.delete(f"/loan/detail_loan/{id}/")

    def get_first_page(self, loan_id):
        return self.get(f"/loan/first_page/{loan_id}")

    def post_first_page(self, loan_id, data):
        return self.post(f"/loan/first_page/{loan_id}", json=data)

    def patch_first_page(self, loan_id, data):
        return self.patch(f"/loan/first_page/{loan_id}", data=data)

    def get_installment_management(self):
        return self.get("/loan/installment_management/")

    def get_installment_management_export(self):
        return self.get("/loan/installment_management/export/")

    def get_list_admin(self):
        return self.get("/loan/list_admin/")

    def post_list_admin(self, data):
        return self.post("/loan/list_admin/", json=data)
    
    def get_list_admin_id(self, id):
        return self.get(f"/loan/list_admin/{id}/")

    def put_list_admin(self, id, data):
        return self.put(f"/loan/list_admin/{id}/", data=data)

    def patch_list_admin(self, id, data):
        return self.patch(f"/loan/list_admin/{id}/", data=data)

    def delete_list_admin(self, id):
        return self.delete(f"/loan/list_admin/{id}/")

    def get_list_assurance(self):
        return self.get("/loan/list_assurance/")

    def post_list_assurance(self, data):
        return self.post("/loan/list_assurance/", json=data)

    def get_list_assurance_id(self, id):
        return self.get(f"/loan/list_assurance/{id}/")

    def put_list_assurance(self, id, data):
        return self.put(f"/loan/list_assurance/{id}/", data=data)

    def patch_list_assurance(self, id, data):
        return self.patch(f"/loan/list_assurance/{id}/", data=data)

    def delete_list_assurance(self, id):
        return self.delete(f"/loan/list_assurance/{id}/")

    def post_login_admin(self, data):
        return self.post("/loan/login_admin/", json=data)

    def get_postponed_facilities(self):
        return self.get("/loan/postponed_facilities/")

    def get_loan_request(self, loan_id, step):
        return self.get(f"/loan/request/{loan_id}/{step}/")

    def post_loan_request(self, loan_id, step, data):
        return self.post(f"/loan/request/{loan_id}/{step}/", json=data)

    def patch_loan_request(self, loan_id, step, data):
        return self.patch(f"/loan/request/{loan_id}/{step}/", data=data)

    def post_retry_credit_rank(self, data):
        return self.post("/loan/retry_credit_rank/", json=data)

    def post_retry_postponed_facility(self, data):
        return self.post("/loan/retry_postponed_facility/", json=data)

    def put_setcode(self, id, data):
        return self.put(f"/loan/setcode/{id}/", data=data)

    def patch_super_admin_admin_user(self, data):
        return self.patch("/loan/super_admin/admin_user/", data=data)

    def post_super_admin_login_as_user(self, data):
        return self.post("/loan/super_admin/login_as_user/", json=data)
    
    def post_user_validation(self, data):
        return self.post("/loan/user_validation/", json=data)

# API client for messages related operations
class MessagesAPI(BaseAPIClient):
    def get_messages(self):
        return self.get("/messages/")

    def get_message(self, id):
        return self.get(f"/messages/{id}/")

    def put_message(self, id, data):
        return self.put(f"/messages/{id}/", data=data)

    def patch_message(self, id, data):
        return self.patch(f"/messages/{id}/", data=data)

# API client for poll related operations
class PollAPI(BaseAPIClient):
    def post_poll(self, data):
        return self.post("/poll/", json=data)

    def get_poll_me(self):
        return self.get("/poll/me/")

    def get_poll_questions(self):
        return self.get("/poll/questions/")

    def get_poll_question(self, id):
        return self.get(f"/poll/questions/{id}/")

# API client for SMS related operations
class SMS_API(BaseAPIClient):
    def get_sms_templates(self):
        return self.get("/sms/templates/")

    def get_sms_template(self, id):
        return self.get(f"/sms/templates/{id}/")

    def put_sms_template(self, id, data):
        return self.put(f"/sms/templates/{id}/", data=data)

    def patch_sms_template(self, id, data):
        return self.patch(f"/sms/templates/{id}/", data=data)

# API client for states related operations
class StatesAPI(BaseAPIClient):
    def get_states(self):
        return self.get("/states/")

# API client for TMS related operations
class TMS_API(BaseAPIClient):
    def get_address_to_location(self, params):
        return self.get("/tms/address_to_location/", params)

    def get_areas(self):
        return self.get("/tms/areas/")

    def get_date_to_daytime(self, params):
        return self.get("/tms/date_to_daytime/", params)

    def get_dgshahr_areas(self):
        return self.get("/tms/dgshahr_areas/")

    def get_location_to_daytime(self, params):
        return self.get("/tms/location_to_daytime/", params)

    def get_logistics(self, params):
        return self.get("/tms/logistics/", params)

    def post_logistics(self, data):
        return self.post("/tms/logistics/", json=data)

    def put_logistics(self, id, data):
        return self.put(f"/tms/logistics/{id}/", data=data)

    def patch_logistics(self, id, data):
        return self.patch(f"/tms/logistics/{id}/", data=data)

    def delete_logistics(self, id):
        return self.delete(f"/tms/logistics/{id}/")

    def get_logistics_pdf(self, id):
        return self.get(f"/tms/logistics/{id}/pdf/")

    def get_logistics_dashboard(self, params):
        return self.get("/tms/logistics/dashboard/", params)

# API client for transaction related operations
class TransactionAPI(BaseAPIClient):
    def post_behpardakht(self, data):
        return self.post("/transaction/behpardakht/", json=data)

# API client for user related operations
class UserAPI(BaseAPIClient):
    def get_login(self):
        return self.get("/user/login/")

    def post_login(self, data):
        return self.post("/user/login/", json=data)

    def post_refresh(self, data):
        return self.post("/user/refresh/", json=data)
