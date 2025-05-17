import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from constants import NATIONAL_CODE, POSTAL_CODE, URL, PHONE_NUMBER, ASSURANCE_CODE
from functions import *


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
        sleep(5)
        login(self.driver, PHONE_NUMBER)
        sleep(5)
        otp_code(self.driver)
        sleep(5)
        guaranty_request(self.driver)
        sleep(3)

    def _upload_documents(self):
        Upload_identity_documents(self.driver, self.file_path_low_size)
        sleep(5)
        next_button(self.driver)

        sleep(3)
        Residence_documents(self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'", "'آدرس تست'", self.file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(self.driver)

        sleep(5)
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)

    def _step_fresh_start(self):
        self._login_and_navigate()
        guaranty_code(self.driver, ASSURANCE_CODE)
        sleep(5)

        primary_info(self.driver, NATIONAL_CODE, "1383", "آبان", "24", "'کارمند رسمی (شرکت دولتی)'", "'سایر'")
        sleep(10)

        self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()
        while not is_credit_approved_in_guaranty_request(self.driver):
            sleep(5)

        sleep(3)
        next_button(self.driver)
        sleep(3)
        self._upload_documents()

    def _step_credit_rank(self):
        self._login_and_navigate()
        sleep(10)
        self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()

        while not is_credit_approved(self.driver):
            sleep(5)

        sleep(3)
        next_button(self.driver)
        sleep(3)
        self._upload_documents()

    def _step_assurance(self):
        self._login_and_navigate()
        self._upload_documents()

    def _step_identity(self):
        self._login_and_navigate()

        Residence_documents(self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'", "'آدرس تست'", self.file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(self.driver)

        sleep(5)
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)

    def _step_residence(self):
        self._login_and_navigate()

        sleep(5)
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)

    def _step_document_check(self):
        self._login_and_navigate()
        sleep(10)


if __name__ == "__main__":
    GuarantyAutomation().run()