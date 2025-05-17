import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
        sleep(5)
        login(self.driver, PHONE_NUMBER)
        sleep(5)
        otp_code(self.driver)
        sleep(5)
        loan_request(self.driver, "Down")
        sleep(3)
        self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button').click()
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
        Residence_documents(
            self.driver, POSTAL_CODE, "'مالک'", "'تهران'", "'تهران'",
            "'آدرس تست'", self.file_path_low_size, "'آدرس تست'"
        )
        sleep(3)
        next_button(self.driver)

        sleep(5)
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)

    def _step_fresh_start(self):
        get_url(self.driver, URL)
        sleep(5)
        login(self.driver, PHONE_NUMBER)
        sleep(5)
        otp_code(self.driver)
        sleep(5)
        loan_request(self.driver, "TOP")
        self.driver.back()
        sleep(2)
        loan_request(self.driver, "Down")

        primary_info(self.driver, NATIONAL_CODE, "1383", "آبان", "24", "'کارمند رسمی (شرکت دولتی)'", "'سایر'")
        sleep(10)
        self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()

        while not is_credit_approved(self.driver):
            sleep(5)
        sleep(3)
        next_button(self.driver)
        sleep(3)

        self._select_guarantee_and_next()
        self._upload_identity_residence_job_docs()

    def _step_auth_otp(self):
        self._login_and_navigate()
        sleep(10)
        self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/button').click()

        while not is_credit_approved(self.driver):
            sleep(5)
        sleep(3)
        next_button(self.driver)
        sleep(3)

        self._select_guarantee_and_next()
        self._upload_identity_residence_job_docs()

    def _step_credit_rank(self):
        self._login_and_navigate()
        self._select_guarantee_and_next()
        self._upload_identity_residence_job_docs()

    def _step_loan_request(self):
        self._login_and_navigate()
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
        Upload_job_documents(self.driver, "'۱۵ تا ۲۰ میلیون تومان'", self.file_path_low_size)
        sleep(3)
        next_button(self.driver)
        sleep(10)

    def _step_branch(self):
        self._login_and_navigate()
        sleep(10)


if __name__ == "__main__":
    LoanAutomation().run()