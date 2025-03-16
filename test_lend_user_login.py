from api_collections import UserAPI
from constants import PHONE_NUMBER
from common_functions import schema_validator, update_token_in_constants
from time import sleep
import pytest



# Test case for sending OTP for the first time
def test_send_otp_first_time():
    data = {"phone_number": PHONE_NUMBER}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending OTP request
    

    assert response.status_code == 200  # Ensuring a successful request

# Test case for sending OTP again when it was already requested
def test_send_otp_second_time():
    data = {"phone_number": PHONE_NUMBER}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending OTP request again
    print(response.status_code)

    assert response.status_code == 200  # Expecting a failure response

def test_send_otp_third_time():
    data = {"phone_number": PHONE_NUMBER}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending OTP request again
    print(response.status_code)

    assert response.status_code == 400  # Expecting a failure response
    assert response.json()["error"] == "کد ورود قبلا ارسال شده است"  # Checking expected error message

# Test case for logging in with the correct OTP
def test_login_correct_otp():
    code = input("Enter OTP Code: ")  # Getting OTP code from user input
    data = {"phone_number": PHONE_NUMBER, "code": code}  # Preparing request payload
    response = UserAPI().post_login(data)  # Sending login request

    assert response.status_code == 200  # Ensuring a successful login

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

    schema_validator(response_body, schema)  # Validating response schema
    update_token_in_constants(response_body["data"]["access_token"])  # Updating token in constants.py


########################################################## Test case for logging in with an incorrect OTP############################################
def test_login_incorrect_otp():
    data = {"phone_number": PHONE_NUMBER, "code": "111111"}  # Providing incorrect OTP
    response = UserAPI().post_login(data)  # Sending login request

    assert response.status_code == 401  # Ensuring the login fails
