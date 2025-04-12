from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from constants import NATIONAL_CODE,  POSTAL_CODE, URL, PHONE_NUMBER, ASSURANCE_CODE
import os
from functions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

global request_step
request_step = None

request_step = get_request_step_guaranty()


chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
file_path_low_size = os.path.abspath("./low_size.png")

match request_step:
    case False:
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### guaranty request page ####################
        guaranty_request(driver)
        sleep(3)
        guaranty_code(driver, ASSURANCE_CODE)
        sleep(5)
        #################### primary info form ####################
        primary_info(driver, NATIONAL_CODE, "1383", "آبان",
                     "24", "'کارمند رسمی (شرکت دولتی)'", "'سایر'")
        #################### Validation ####################
        sleep(10)
        exit_button = driver.find_element(
            By.XPATH, '/html/body/div[2]/div/div/div[1]/button')
        exit_button.click()

        while not is_credit_approved_in_guaranty_request(driver):
            sleep(5)
        sleep(3)
        next_button(driver)
        sleep(3)
        #################### identity_documents ####################
        Upload_identity_documents(driver, file_path_low_size)
        sleep(5)
        next_button(driver)
        #################### Residence_documents ####################
        sleep(3)
        Residence_documents(driver, POSTAL_CODE, "'مالک'", "'تهران'",
                            "'تهران'", "'آدرس تست'", file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(driver)
        #################### job_documents ####################
        sleep(5)
        Upload_job_documents(
            driver, "'۱۵ تا ۲۰ میلیون تومان'", file_path_low_size)
        sleep(3)
        next_button(driver)
        ####################
        sleep(10)

    case "primary_info_registration__credit_rank":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### guaranty request page ####################
        guaranty_request(driver)
        sleep(3)
        #################### Validation ####################
        sleep(10)
        exit_button = driver.find_element(
            By.XPATH, '/html/body/div[2]/div/div/div[1]/button')
        exit_button.click()
        while not is_credit_approved(driver):
            sleep(5)
        sleep(3)
        next_button(driver)
        sleep(3)
        #################### identity_documents ####################
        Upload_identity_documents(driver, file_path_low_size)
        sleep(5)
        next_button(driver)
        #################### Residence_documents ####################
        sleep(3)
        Residence_documents(driver, POSTAL_CODE, "'مالک'", "'تهران'",
                            "'تهران'", "'آدرس تست'", file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(driver)
        #################### job_documents ####################
        sleep(5)
        Upload_job_documents(
            driver, "'۱۵ تا ۲۰ میلیون تومان'", file_path_low_size)
        sleep(3)
        next_button(driver)
        ####################
        sleep(10)

    case "assurance_request":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### guaranty request page ####################
        guaranty_request(driver)
        sleep(3)
        #################### identity_documents ####################
        Upload_identity_documents(driver, file_path_low_size)
        sleep(5)
        next_button(driver)
        #################### Residence_documents ####################
        sleep(3)
        Residence_documents(driver, POSTAL_CODE, "'مالک'", "'تهران'",
                            "'تهران'", "'آدرس تست'", file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(driver)
        #################### job_documents ####################
        sleep(5)
        Upload_job_documents(
            driver, "'۱۵ تا ۲۰ میلیون تومان'", file_path_low_size)
        sleep(3)
        next_button(driver)
        ####################
        sleep(10)

    case "info_completion__identity":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### guaranty request page ####################
        guaranty_request(driver)
        sleep(3)
        #################### Residence_documents ####################
        Residence_documents(driver, POSTAL_CODE, "'مالک'", "'تهران'",
                            "'تهران'", "'آدرس تست'", file_path_low_size, "'آدرس تست'")
        sleep(3)
        next_button(driver)
        #################### job_documents ####################
        sleep(5)
        Upload_job_documents(
            driver, "'۱۵ تا ۲۰ میلیون تومان'", file_path_low_size)
        sleep(3)
        next_button(driver)
        ####################
        sleep(10)

    case "info_completion__residence":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### guaranty request page ####################
        guaranty_request(driver)
        sleep(3)
        #################### job_documents ####################
        sleep(5)
        Upload_job_documents(
            driver, "'۱۵ تا ۲۰ میلیون تومان'", file_path_low_size)
        sleep(3)
        next_button(driver)
        ####################
        sleep(10)

    case "document_check":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### guaranty request page ####################
        guaranty_request(driver)
        sleep(3)
        ####################
        sleep(10)
