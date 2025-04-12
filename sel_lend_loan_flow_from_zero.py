from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from constants import NATIONAL_CODE, MAX_VALUE, POSTAL_CODE, URL, PHONE_NUMBER
import os
from functions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

global request_step
request_step = None

request_step = get_request_step_loan()


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
        #################### loan request page ####################
        loan_request(driver, "TOP")
        driver.back()
        sleep(2)
        loan_request(driver, "Down")

        #################### primary info form ####################
        primary_info(driver, NATIONAL_CODE, "1383", "آبان",
                     "24", "'کارمند رسمی (شرکت دولتی)'", "'سایر'")
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
        #################### guarantee ####################
        select_guarantee_type(driver, "'دو برگ چک صیادی خودم'")
        sleep(2)
        set_max_value(driver, MAX_VALUE)
        period_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'swiper-slide-next') and contains(@class, 'select-none')]//span[@class='period-value' and text()='24']")
        period_element.click()
        checkbox1 = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[1]/div/div[2]/div/span/span[1]')
        checkbox1.click()
        checkbox2 = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[2]/div/div[2]/div/span/span/span[1]')
        checkbox2.click()
        sleep(2)
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

    case "primary_info_registration__auth_otp":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### loan ####################
        loan_request(driver, "Down")
        sleep(3)
        auth_button = driver.find_element(
            By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button')
        auth_button.click()
        sleep(3)
        ####################
        sleep(10)
        exit_button = driver.find_element(
            By.XPATH, '/html/body/div[2]/div/div/div[1]/button')
        exit_button.click()
        while not is_credit_approved(driver):
            sleep(5)
        sleep(3)
        next_button(driver)
        sleep(3)
        #################### guarantee ####################
        select_guarantee_type(driver, "'دو برگ چک صیادی خودم'")
        sleep(2)
        set_max_value(driver, MAX_VALUE)
        period_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'swiper-slide-next') and contains(@class, 'select-none')]//span[@class='period-value' and text()='24']")
        period_element.click()
        checkbox1 = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[1]/div/div[2]/div/span/span[1]')
        checkbox1.click()
        checkbox2 = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[2]/div/div[2]/div/span/span/span[1]')
        checkbox2.click()
        sleep(2)
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
        #################### loan ####################
        loan_request(driver, "Down")
        sleep(3)
        auth_button = driver.find_element(
            By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button')
        auth_button.click()
        sleep(3)
        #################### guarantee ####################
        select_guarantee_type(driver, "'دو برگ چک صیادی خودم'")
        sleep(2)
        set_max_value(driver, MAX_VALUE)
        period_element = driver.find_element(
            By.XPATH, "//div[contains(@class, 'swiper-slide-next') and contains(@class, 'select-none')]//span[@class='period-value' and text()='24']")
        period_element.click()
        checkbox1 = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[1]/div/div[2]/div/span/span[1]')
        checkbox1.click()
        checkbox2 = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[5]/label[2]/div/div[2]/div/span/span/span[1]')
        checkbox2.click()
        sleep(2)
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
    case "loan_request":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### loan ####################
        loan_request(driver, "Down")
        sleep(3)
        auth_button = driver.find_element(
            By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button')
        auth_button.click()
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
        #################### loan ####################
        loan_request(driver, "Down")
        sleep(3)
        auth_button = driver.find_element(
            By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button')
        auth_button.click()
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
        #################### loan ####################
        loan_request(driver, "Down")
        sleep(3)
        auth_button = driver.find_element(
            By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button')
        auth_button.click()
        #################### job_documents ####################
        sleep(5)
        Upload_job_documents(
            driver, "'۱۵ تا ۲۰ میلیون تومان'", file_path_low_size)
        sleep(3)
        next_button(driver)
        ####################
        sleep(10)
    case "info_completion__branch":
        get_url(driver, URL)
        sleep(5)
        #################### login page ####################
        login(driver, PHONE_NUMBER)
        sleep(5)
        #################### otp code ####################
        code = otp_code(driver)
        sleep(5)
        #################### loan ####################
        loan_request(driver, "Down")
        sleep(3)
        auth_button = driver.find_element(
            By.XPATH, '/html/body/div/div[2]/div/div[2]/div/a/button')
        auth_button.click()
        ####################
        sleep(10)
