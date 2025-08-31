import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from constants import *
from functions import *
from TCMS_tools.tcms_fuctions import *
from tcms_api import TCMS
import TCMS_tools.tcms_maps as tcms_maps
import datetime

# TCMS setup
tcms_url = TCMS_URL
tcms_username = TCMS_USERNAME
tcms_password = TCMS_PASSWORD
rpc = TCMS(tcms_url, tcms_username, tcms_password).exec

# -------------------- create Test Run & add cases --------------------
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

test_run_data = {
    "summary": f"selenium_lend_assurancce_flow {now_str}",
    "plan": tcms_maps.TEST_PLANS["LEND_USER_ASSURANCE_FRONTEND"],
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
test_cases = rpc.TestCase.filter({"plan": tcms_maps.TEST_PLANS["LEND_USER_ASSURANCE_FRONTEND"]})
for case in test_cases:
    rpc.TestRun.add_case(runner_id, case["id"])


class GuarantyAutomation:
    def __init__(self):
        self.driver = self._setup_driver()
        self.file_path_low_size = os.path.abspath("./low_size.png")
        self.request_step = get_request_step_guaranty()

    def _setup_driver(self):
        options = Options()
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    def check_current_url(self, expected_url, testcase_name):
        """Function to check if the current URL matches the expected URL and print a message."""
        current_url = self.driver.current_url
        print(current_url)
        set_exec_status(rpc , runner_id ,testcase_name, current_url.startswith(expected_url))
        
    def convert_birthdate_to_detail(birth_date: str):
        date_parts = birth_date.split('/')
        year, month, day = map(int, date_parts)

        months_farsi = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر", 
            5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 
            9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
        }
        return str(year), str(months_farsi[month]) , str(day)

    def run(self):
        step_methods = {
            False: self._step_fresh_start,
            "primary_info_registration__credit_rank": self._step_credit_rank,
            "assurance_request": self._step_assurance,
            "info_completion__identity": self._step_identity,
            "info_completion__residence": self._step_residence,
            "document_check": self._step_document_check
        }

        action = step_methods.get(self.request_step)
        if action:
            action()
        else:
            print(f"❌ Unknown request step: {self.request_step}")

    def _login_and_navigate(self):
        get_url(self.driver, URL)
        self.check_current_url(URL , "get_URL")
        sleep(5)
        login(self.driver, PHONE_NUMBER)
        sleep(5)
        otp_code(self.driver)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "login")
        guaranty_request(self.driver)
        sleep(3)

    def _upload_documents(self):
        Upload_identity_documents(self.driver, self.file_path_low_size)
        sleep(5)
        next_button(self.driver)
        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor/residence-document" , "Upload_identity_documents")

        Residence_documents(self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'", "'آدرس تست'", self.file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(self.driver)

        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor/employment-document" , "Residence_documents")
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)

    def _step_fresh_start(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/" ,"login_and_navigate" )
        add_comment_to_tcms(rpc , runner_id , "login_and_navigate" , "login_and_navigate_to_guaranty_code")

        guaranty_code(self.driver, ASSURANCE_CODE)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor/personal-info/" , "guaranty_code")
        year , month , day = self.convert_birthdate_to_detail(BIRTH_DATE)
        primary_info(self.driver, NATIONAL_CODE, year,month,day, "'کارمند رسمی (شرکت دولتی)'", "'سایر'")
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor/credit-rank/" ,"primary_info_page")
        sleep(10)

        try:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()
            set_exec_status_manualy(rpc,runner_id,"cross_button","PASSED")
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            set_exec_status_manualy(rpc,runner_id,"cross_button","FAILED")
            add_failure_comment_to_tcms(rpc , runner_id , "cross_button" , str(e))


        while not is_credit_approved_in_guaranty_request(self.driver):
            sleep(5)
            set_exec_status_manualy(rpc , runner_id ,"is_credit_approved" , "RUNNING")
        sleep(3)
        if is_credit_approved_in_guaranty_request(self.driver) == True:
            set_exec_status_manualy(rpc , runner_id ,"is_credit_approved" , "PASSED")
        #TODO : if next button error
        next_button(self.driver)
        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor/identity-document" , "credit_rank_page")
        self._upload_documents()
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "Upload_job_documents_page")
        sleep(10)
        update_tests_not_in_scenario(rpc , runner_id)

    def _step_credit_rank(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" ,"login_and_navigate" )
        add_comment_to_tcms(rpc , runner_id , "login_and_navigate" , "login_and_navigate_to_guarantor_list")
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" , "guarantor-list")
        continue_process(self.driver)
        sleep(10)
        try:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()
            set_exec_status_manualy(rpc,runner_id,"cross_button","PASSED")
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            set_exec_status_manualy(rpc,runner_id,"cross_button","FAILED")
            add_failure_comment_to_tcms(rpc , runner_id , "cross_button" , str(e))

        while not is_credit_approved_in_guaranty_request(self.driver):
            sleep(5)
            set_exec_status_manualy(rpc , runner_id ,"is_credit_approved" , "RUNNING")
        sleep(3)
        if is_credit_approved_in_guaranty_request(self.driver) == True:
            set_exec_status_manualy(rpc , runner_id ,"is_credit_approved" , "PASSED")
        #TODO : if next button error
        next_button(self.driver)
        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor/identity-document" , "credit_rank_page")
        self._upload_documents()
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "Upload_job_documents_page") 
        sleep(10)
        update_tests_not_in_scenario(rpc , runner_id)

    def _step_assurance(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" ,"login_and_navigate" )
        add_comment_to_tcms(rpc , runner_id , "login_and_navigate" , "login_and_navigate_to_guarantor_list")
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" , "guarantor-list")
        continue_process(self.driver)
        self._upload_documents()
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "Upload_job_documents_page")
        sleep(10)
        update_tests_not_in_scenario(rpc , runner_id)

    def _step_identity(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" ,"login_and_navigate" )
        add_comment_to_tcms(rpc , runner_id , "login_and_navigate" , "login_and_navigate_to_guarantor_list")
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" , "guarantor-list")
        continue_process(self.driver)

        Residence_documents(self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'", "'آدرس تست'", self.file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(self.driver)
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor/employment-document" , "Residence_documents")

        sleep(5)
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "Upload_job_documents_page")
        sleep(10)
        update_tests_not_in_scenario(rpc , runner_id)

    def _step_residence(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" ,"login_and_navigate" )
        add_comment_to_tcms(rpc , runner_id , "login_and_navigate" , "login_and_navigate_to_guarantor_list")
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" , "guarantor-list")
        continue_process(self.driver)

        sleep(5)
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "Upload_job_documents_page")
        sleep(10)
        update_tests_not_in_scenario(rpc , runner_id)

    def _step_document_check(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" ,"login_and_navigate" )
        add_comment_to_tcms(rpc , runner_id , "login_and_navigate" , "login_and_navigate_to_guarantor_list")
        self.check_current_url("https://alpha.dgstack.ir/lend/guarantor-list" , "guarantor-list")
        sleep(10)
        update_tests_not_in_scenario(rpc , runner_id)


if __name__ == "__main__":
    GuarantyAutomation().run()

    rpc.TestRun.update(runner_id , {
        'stop_date' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })