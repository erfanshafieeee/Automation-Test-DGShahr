import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

from constants import NATIONAL_CODE, MAX_VALUE, POSTAL_CODE, URL, PHONE_NUMBER
from functions import *


class LoanAutomation:
    def __init__(self):
        self.driver = self._setup_driver()
        self.file_path_low_size = os.path.abspath("./low_size.png")
        self.request_step = get_request_step_loan()

    def _setup_driver(self):
        options = Options()
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    

    def check_current_url(self, expected_url, message):
        """Function to check if the current URL matches the expected URL and print a message."""
        current_url = self.driver.current_url
        print(current_url)
        if current_url.startswith(expected_url):
            print(f"###################### {message} = pass ###################")

    def run(self):
        step_methods = {
            False: self._step_fresh_start,
            "primary_info_registration__auth_otp": self._step_auth_otp,
            "primary_info_registration__credit_rank": self._step_credit_rank,
            "loan_request": self._step_loan_request,
            "info_completion__identity": self._step_identity,
            "info_completion__residence": self._step_residence,
            "info_completion__branch": self._step_branch,
        }

        action = step_methods.get(self.request_step)
        if action:
            action()
        else:
            print(f"❌ Unknown request step: {self.request_step}")

    def _login_and_navigate(self):
        get_url(self.driver, URL)
        self.check_current_url(URL , "get url")
        sleep(5)
        login(self.driver, PHONE_NUMBER)
        sleep(5)
        otp_code(self.driver)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "login")
        loan_request(self.driver, "Down")
        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/" , "loan_request_down")
        try:
            self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button').click()
            print("###################### countiue_button = pass ###################")
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            print("###################### countiue_button = fail ###################", e)
        sleep(3)

    def _select_guarantee_and_next(self):
        select_guarantee_type(self.driver, "'دو برگ چک صیادی خودم'")
        sleep(2)
        set_max_value(self.driver, MAX_VALUE)
        self.driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'swiper-slide-next')]//span[text()='24']"
        ).click()
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[1]//span/span[1]').click()
        self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[2]//span/span/span[1]').click()
        sleep(2)
        next_button(self.driver)
        sleep(3)
        

    def _upload_identity_residence_job_docs(self):
        Upload_identity_documents(self.driver, self.file_path_low_size)
        sleep(5)
        next_button(self.driver)

        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/residence-document/" , "identity_documents")
        Residence_documents(
            self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'",
            "'آدرس تست'", self.file_path_low_size, "'آدرس تست'"
        )
        sleep(3)
        next_button(self.driver)

        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/employment-document/" , "Residence_documents")
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)

    def _step_fresh_start(self):
        get_url(self.driver, URL)
        self.check_current_url(URL , "get url")
        sleep(5)
        login(self.driver, PHONE_NUMBER)
        sleep(5)
        otp_code(self.driver)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/" , "login")
        loan_request(self.driver, "TOP")
        self.check_current_url("https://alpha.dgstack.ir/lend/user/personal-info/" , "loan_request_top")
        self.driver.back()
        sleep(2)
        loan_request(self.driver, "Down")
        self.check_current_url("https://alpha.dgstack.ir/lend/user/personal-info/" , "loan_request_down")
        primary_info(self.driver, NATIONAL_CODE, "1383", "آبان", "24", "'کارمند رسمی (شرکت دولتی)'", "'سایر'")
        self.check_current_url("https://alpha.dgstack.ir/lend/user/credit-rank/" , "primary_info")
        sleep(10)
        try:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()
            print("###################### cross_button = pass ###################")
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            print("###################### cross_button = fail ###################", e)
        
        while not is_credit_approved(self.driver):
            sleep(5)
            print("###################### is_credit_approved = RUNNING ###################")
        sleep(3)
        if is_credit_approved(self.driver) == True:
            print("###################### is_credit_approved = pass ###################")
        next_button(self.driver)
        #todo : if next button error
        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-request/" , "credit_rank_page")
        self._select_guarantee_and_next()
        self.check_current_url("https://alpha.dgstack.ir/lend/user/identity-document/" , "gurantee_page")
        self._upload_identity_residence_job_docs()
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/" , "Upload_job_documents")


    def _step_auth_otp(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/user/credit-rank/" , "login_and_navigate_to_credit_rank")
        sleep(10)
        try:
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()
            print("###################### cross_button = pass ###################")
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            print("###################### cross_button = fail ###################", e)

        while not is_credit_approved(self.driver):
            sleep(5)
            print("###################### is_credit_approved = RUNNING ###################")
        sleep(3)
        if is_credit_approved(self.driver) == True:
            print("###################### is_credit_approved = pass ###################")
        next_button(self.driver)
        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-request/" , "credit_rank_page" )
        self._select_guarantee_and_next()
        self.check_current_url("https://alpha.dgstack.ir/lend/user/identity-document/" ,"gurantee_page" )
        self._upload_identity_residence_job_docs()
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/" ,"Upload_job_documents" )

    def _step_credit_rank(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-request/" ,"_login_and_navigate_to_loan-request" )
        self._select_guarantee_and_next()
        self.check_current_url("https://alpha.dgstack.ir/lend/user/identity-document/" ,"gurantee_page")
        self._upload_identity_residence_job_docs()
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/" , "Upload_job_documents")

    def _step_loan_request(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/user/identity-document/" ,"_login_and_navigate_to_identity_page")
        Upload_identity_documents(self.driver, self.file_path_low_size)
        sleep(5)
        next_button(self.driver)
        sleep(3)
        self.check_current_url("https://alpha.dgstack.ir/lend/residence-document/" , "identity_documents")
        Residence_documents(self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'", "'آدرس تست'", self.file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(self.driver)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/employment-document/" , "Residence_documents")
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/","Upload_job_documents")

    def _step_identity(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/residence-document/" , "login_and_navigate_to_residence-document")
        Residence_documents(self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'", "'آدرس تست'", self.file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(self.driver)
        sleep(5)
        self.check_current_url("https://alpha.dgstack.ir/lend/employment-document/" , "Residence_documents" )
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/" ,"Upload_job_documents")

    def _step_residence(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/employment-document/" , "login_and_navigate_to_employment-document")
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/" , "Upload_job_documents")


    def _step_branch(self):
        self._login_and_navigate()
        self.check_current_url("https://alpha.dgstack.ir/lend/loan-info/" , "loan_info_last_page")
        sleep(10)


if __name__ == "__main__":
    LoanAutomation().run()