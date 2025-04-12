# Import required libraries
from selenium.webdriver.common.by import By
import psycopg2
from time import sleep


# Navigate to specified URL
def get_url(driver, url):
    driver.get(url)


# Handle login with phone number
def login(driver, Phone_number):
    Phone_number_box = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[2]/div/div[2]/input')
    Phone_number_box.clear()
    Phone_number_box.send_keys(Phone_number)
    get_code_button = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/div[2]/button')
    get_code_button.click()


# Handle OTP verification
def otp_code(driver):
    digit_1 = driver.find_element(By.ID, 'dgs-ui-kit-otp-input-0')
    otp_code = input("please enter your otp code : ")
    digit_1.send_keys(otp_code)
    return otp_code


# Handle loan request button clicks
def loan_request(driver, button_type):
    if button_type == "TOP":
        loan_request_button_top = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div[2]/a/button')
        loan_request_button_top.click()
    elif button_type == "Down":
        loan_request_button_down = driver.find_element(
            By.XPATH, '/html/body/div[1]/div[2]/div/div/div[3]/div/button[1]')
        loan_request_button_down.click()
    else:
        print("The input is invalid.")


# Handle guaranty request button click
def guaranty_request(driver):
    guaranty_request_button_down = driver.find_element(
        By.XPATH, '/html/body/div/div[2]/div/div/div[3]/div/button[2]')
    guaranty_request_button_down.click()


# Handle guaranty code submission
def guaranty_code(driver, guaranty_code):
    guaranty_code_box = driver.find_element(
        By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div[2]/input')
    guaranty_code_box.send_keys(guaranty_code)
    sleep(2)
    guaranty_code_submit_button = driver.find_element(
        By.XPATH, '/html/body/div[2]/div/div/div[2]/div/button')
    guaranty_code_submit_button.click()
    sleep(3)
    start_button = driver.find_element(
        By.XPATH, '/html/body/div[2]/div/div/div[3]/a/button')
    start_button.click()


# Handle birth date selection
def birth_date(driver, target_year, target_month, target_day):
    months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
              "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]

    birth_date_box = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div[1]/div/div[2]/div/div[2]/input')
    birth_date_box.click()

    sleep(3)
    current_day = driver.find_element(
        By.CSS_SELECTOR, ".swiper-slide-active span").text
    current_month = driver.find_elements(
        By.CSS_SELECTOR, ".swiper-slide-active span")[1].text
    current_year = driver.find_elements(
        By.CSS_SELECTOR, ".swiper-slide-active span")[2].text
    day_up = driver.find_elements(By.CSS_SELECTOR, ".button-medium-icon")[0]
    day_down = driver.find_elements(By.CSS_SELECTOR, ".button-medium-icon")[1]
    month_up = driver.find_elements(By.CSS_SELECTOR, ".button-medium-icon")[2]
    month_down = driver.find_elements(
        By.CSS_SELECTOR, ".button-medium-icon")[3]
    year_up = driver.find_elements(By.CSS_SELECTOR, ".button-medium-icon")[4]
    year_down = driver.find_elements(By.CSS_SELECTOR, ".button-medium-icon")[5]
    current_day = int(current_day)
    target_day = int(target_day)

    if current_day < target_day:
        for _ in range(target_day - current_day):
            day_down.click()
            sleep(0.2)
    else:
        for _ in range(current_day - target_day):
            day_up.click()
            sleep(0.2)

    current_month_index = months.index(current_month)
    target_month_index = months.index(target_month)

    if current_month_index < target_month_index:
        for _ in range(target_month_index - current_month_index):
            month_down.click()
            sleep(0.2)
    else:
        for _ in range(current_month_index - target_month_index):
            month_up.click()
            sleep(0.2)

    current_year = int(current_year)
    target_year = int(target_year)

    if current_year < target_year:
        for _ in range(target_year - current_year):
            year_down.click()
            sleep(0.2)
    else:
        for _ in range(current_year - target_year):
            year_up.click()
            sleep(0.2)

    confirm_birth_date_button = driver.find_element(
        By.XPATH, "//button[contains(., 'تایید')]")
    confirm_birth_date_button.click()


# Handle primary information form
def primary_info(driver, national_code, target_year, target_month, target_day, Job_position_option, Organization_option):
    national_code_box = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/div[2]/input')
    national_code_box.send_keys(national_code)

    birth_date(driver, target_year, target_month, target_day)

    Job_position_box = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div[1]/div/div[3]/div/div[2]/input')
    Job_position_box.click()
    sleep(2)
    Job_position_option_box = driver.find_element(
        By.XPATH, f"//button[contains(text(), {Job_position_option})]")
    Job_position_option_box.click()

    Organization_box = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div[1]/div/div[4]/div/div[2]/input')
    Organization_box.click()
    sleep(2)
    Organization_option = driver.find_element(
        By.XPATH, f"//button[contains(text(), {Organization_option})]")
    Organization_option.click()

    Information_recording_button = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div[2]/button')
    Information_recording_button.click()


# Check if credit is approved for loan
def is_credit_approved(driver):
    try:
        driver.find_element(
            By.XPATH, "//div[contains(text(), 'مجاز برای دریافت وام')]")
        return True
    except:
        return False


# Check if credit is approved for guaranty
def is_credit_approved_in_guaranty_request(driver):
    try:
        driver.find_element(
            By.XPATH, "//div[contains(text(), 'مجاز برای ضمانت')]")
        return True
    except:
        return False


# Handle next button click
def next_button(driver):
    next_button = driver.find_element(
        By.XPATH, "//button[div[text()='مرحله بعدی']]")
    next_button.click()


# Handle guarantee type selection
def select_guarantee_type(driver, guarantee_type):
    show_guarantee = driver.find_element(
        By.XPATH, "//button[div[contains(text(), 'مشاهده ضمانت')]]")
    show_guarantee.click()
    sleep(2)
    guarantee = driver.find_element(
        By.XPATH, f"//*[contains(text(), {guarantee_type})]")
    guarantee.click()
    sleep(2)
    confirm_garantee = driver.find_element(
        By.XPATH, "//button[div[text()='تایید']]")
    confirm_garantee.click()


# Convert Persian numbers to integers
def convert_persian_to_int(num_str):
    mapping = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        '٬': ''  # حذف کاماها
    }
    result = ""
    for ch in num_str:
        result += mapping.get(ch, ch)
    try:
        return int(result)
    except ValueError:
        return 0


# Set maximum loan value
def set_max_value(driver, max_value):
    loan_input = driver.find_element(
        By.XPATH, "//div[contains(@class, 'dgs-ui-kit-relative')]/input")

    current_value_str = loan_input.get_attribute("value")
    current_value = convert_persian_to_int(current_value_str)

    plus_button = driver.find_element(
        By.CSS_SELECTOR, "div.flex.items-center.justify-center.h-fit.w-fit > button:first-of-type")
    plus_button.click()

    while current_value < max_value:
        plus_button.click()
        sleep(0.2)
        current_value_str = loan_input.get_attribute("value")
        current_value = convert_persian_to_int(current_value_str)


# Handle identity document uploads
def Upload_identity_documents(driver, file_path):
    front_national_cart_input = driver.find_element(
        By.XPATH, "//input[@type='file' and contains(@accept, 'image/png')]")
    back_national_cart_input = driver.find_element(
        By.XPATH, "(//input[@type='file'])[2]")
    Birth_certificate_file_inputs = driver.find_elements(
        By.XPATH, "//h2[contains(text(), 'بارگذاری تصاویر شناسنامه')]/following::input[@type='file']")
    front_national_cart_input.send_keys(file_path)
    back_national_cart_input.send_keys(file_path)
    Birth_certificate_file_inputs[0].send_keys(file_path)
    Birth_certificate_file_inputs[1].send_keys(file_path)
    Birth_certificate_file_inputs[2].send_keys(file_path)


# Handle residence document uploads and form
def Residence_documents(driver, postal_code, Residence_status_type, Province_type, city_type, Residential_address, file_path, Work_address):
    Residence_status = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[1]/div[2]/div/div[2]/input')
    Residence_status.click()
    sleep(2)
    Residence_option = driver.find_element(
        By.XPATH, f"//button[contains(text(), {Residence_status_type})]")
    Residence_option.click()
    Province = driver.find_element(
        By.XPATH, '//*[@id="layout-container"]/div/div[2]/div[1]/div[3]/div/div[2]/input')
    Province.click()
    sleep(2)
    select_Province = driver.find_element(
        By.XPATH, f"//button[contains(text(), {Province_type})]")
    select_Province.click()
    city = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[1]/div[4]/div/div[2]/input')
    city.click()
    sleep(2)
    select_city = driver.find_element(
        By.XPATH, f"//button[contains(text(), {city_type})]")
    select_city.click()
    sleep(2)
    residential_address = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div[2]/textarea')
    residential_address.send_keys(Residential_address)
    Document_of_house_upload = driver.find_element(
        By.XPATH, "//h2[contains(text(), 'بارگذاری تصویر سند یا اجاره نامه محل سکونت')]/following::input[@type='file'][1]")
    Document_of_house_upload.send_keys(file_path)
    work_address = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[4]/div[2]/textarea')
    work_address.send_keys(Work_address)
    postal_code_box = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[1]/div[1]/div[2]/input')
    postal_code_box.send_keys(postal_code)


# Handle job document uploads
def Upload_job_documents(driver, Average_income, file_path):
    Average_income_box = driver.find_element(
        By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div/div[1]/div[1]/button/div/div[2]/input')
    Average_income_box.click()
    sleep(3)
    select_Average_income = driver.find_element(
        By.XPATH, f"//button[contains(text(), {Average_income})]")
    select_Average_income.click()
    Document_of_job_upload = driver.find_elements(
        By.XPATH, "//h2[contains(text(), 'بارگذاری تصاویر مدارک شغلی')]/following::input[@type='file']")
    Document_of_job_upload[0].send_keys(file_path)
    Document_of_job_upload[1].send_keys(file_path)


# Get loan request step from database
def get_request_step_loan():
    try:
        conn = psycopg2.connect(
            host="db.dgstack.ir",
            port="5433",
            database="lend",
            user="lend_developer",
            password="!@#develop123"
        )
        if conn and conn.status == psycopg2.extensions.STATUS_READY:
            print("Successfully connected to the database.")
        else:
            print("Failed to connect to the database.")

        cursor = conn.cursor()

        query_request_step = """
        SELECT l.request_step
        FROM user_user u
        LEFT JOIN lend_loan l ON u.id = l.user_id
        WHERE u.phone_number = '09332766613'
          AND u.is_deleted = false
          AND (l.is_deleted = false)
        LIMIT 1;
        """

        cursor.execute(query_request_step)

        result = cursor.fetchone()

        if result:
            request_step = result[0]
            print(request_step)
            return request_step
        else:
            request_step = False
            print(request_step)
            return request_step

    except psycopg2.Error as e:
        print("Error while updating the database:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            if conn.closed:
                print("Successfully disconnected from the database.")
            else:
                print("Disconnection failed.")



# Get guaranty request step from database
def get_request_step_guaranty():
    try:
        conn = psycopg2.connect(
            host="db.dgstack.ir",
            port="5433",
            database="lend",
            user="lend_developer",
            password="!@#develop123"
        )
        if conn and conn.status == psycopg2.extensions.STATUS_READY:
            print("Successfully connected to the database.")
        else:
            print("Failed to connect to the database.")

        cursor = conn.cursor()

        query_request_step_guaranty = """
        SELECT a.request_step
        FROM user_user u
        LEFT JOIN assurance_assurance a ON u.id = a.user_id
        WHERE u.phone_number = '09332766613'
          AND u.is_deleted = false
          AND (a.is_deleted = false)
        LIMIT 1;
        """
        cursor.execute(query_request_step_guaranty)

        result = cursor.fetchone()

        if result:
            request_step = result[0]
            print(request_step)
            return request_step
        else:
            request_step = False
            print(request_step)
            return request_step

    except psycopg2.Error as e:
        print("Error while updating the database:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            if conn.closed:
                print("Successfully disconnected from the database.")
            else:
                print("Disconnection failed.")


def set_as_new_loan_user():
    try:
        conn = psycopg2.connect(
            host="db.dgstack.ir",
            port="5433",
            database="lend",
            user="lend_developer",
            password="!@#develop123"
        )
        if conn and conn.status == psycopg2.extensions.STATUS_READY:
            print("Successfully connected to the database.")
        else:
            print("Failed to connect to the database.")
        cursor = conn.cursor()

        query_set_as_new_user = """
        UPDATE user_user
        SET is_deleted = true
        WHERE phone_number = %s;
        """
        phone_number = '09332766613'

        cursor.execute(query_set_as_new_user, (phone_number,))
        conn.commit()  # Important: Commit the transaction

        print("Update successful")

    except psycopg2.Error as e:
        print("Error while updating the database:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            if conn.closed:
                print("Successfully disconnected from the database.")
            else:
                print("Disconnection failed.")



def set_as_new_assurance_user():
    try:
        conn = psycopg2.connect(
            host="db.dgstack.ir",
            port="5433",
            database="lend",
            user="lend_developer",
            password="!@#develop123"
        )
        if conn and conn.status == psycopg2.extensions.STATUS_READY:
            print("Successfully connected to the database.")
        else:
            print("Failed to connect to the database.")
        cursor = conn.cursor()

        query_set_as_new_assurance_user = """
        UPDATE assurance_assurance
        SET is_deleted = TRUE
        FROM lend_loan
        WHERE assurance_assurance.loan_id = lend_loan.id
        AND lend_loan.id = %s;
        """
        lend_loan_id = '10920'

        cursor.execute(query_set_as_new_assurance_user, (lend_loan_id,))
        conn.commit()  # Important: Commit the transaction

        print("Update successful")

    except psycopg2.Error as e:
        print("Error while updating the database:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            if conn.closed:
                print("Successfully disconnected from the database.")
            else:
                print("Disconnection failed.")

def set_pro_user():
    try:
        conn = psycopg2.connect(
            host="db.dgstack.ir",
            port="5433",
            database="lend",
            user="lend_developer",
            password="!@#develop123"
        )
        if conn and conn.status == psycopg2.extensions.STATUS_READY:
            print("Successfully connected to the database.")
        else:
            print("Failed to connect to the database.")
        cursor = conn.cursor()

        query_set_as_pro_user = """
        UPDATE assurance_assurance
        SET credit_rank = 'A', credit_score = 660 , status = 'document_check'
        FROM user_user
        WHERE assurance_assurance.user_id = user_user.id
        AND user_user.phone_number = '09332766613';
        """
        phone_number = '09332766613'

        cursor.execute(query_set_as_pro_user, (phone_number,))
        conn.commit()  # Important: Commit the transaction

        print("Update successful")

    except psycopg2.Error as e:
        print("Error while updating the database:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            if conn.closed:
                print("Successfully disconnected from the database.")
            else:
                print("Disconnection failed.")

