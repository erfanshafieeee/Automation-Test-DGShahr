import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from constants import PHONE_NUMBER
from functions import get_url


class DriverFactory:
    @staticmethod
    def create() -> webdriver.Chrome:
        options = Options()
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--remote-allow-origins=*')
        # options.add_argument('--headless')  # Uncomment for headless mode
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


class MarketplaceCheckoutTester:
    def __init__(self, product_url: str):
        self.product_url = product_url
        self.driver = DriverFactory.create()
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        get_url(self.driver, "https://marketplace-staging.dgstack.ir/shop")
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[p[normalize-space(text())='ثبت‌نام'] and p[normalize-space(text())='ورود']]"
        ))).click()

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#phone"))).send_keys(PHONE_NUMBER)

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[div[normalize-space(text())='دریافت کد']]"
        ))).click()

        sleep(2)
        otp = input("Enter OTP code: ")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#dgs-ui-kit-otp-input-0"))).send_keys(otp)

        sleep(5)
        get_url(self.driver, "https://marketplace-staging.dgstack.ir/shop")
        print("✅ Logged in successfully")

    def add_to_cart(self) -> bool:
        get_url(self.driver, self.product_url)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        sleep(0.5)

        if self.driver.find_elements(By.CSS_SELECTOR, "select, .variant-selector, .product-options"):
            print(f"⚠️ Skipping variant-selection product: {self.product_url}")
            return False

        buttons = self.driver.find_elements(
            By.XPATH,
            "//button[.//div[normalize-space(text())='افزودن به سبد خرید']]"
        )
        if not buttons:
            print(f"⚠️ No add-to-cart button found: {self.product_url}")
            return False

        btn = buttons[0]
        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        btn.click()

        try:
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH,
                "//p[normalize-space(text())='به سبد خرید اضافه شد']"
            )))
            print(f"✅ Product added: {self.product_url}")
            return True
        except TimeoutException:
            print(f"⚠️ No confirmation modal for: {self.product_url}")
            return False

    def proceed_to_payment(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.mgc_shopping_cart_2_line"))).click()
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//div[normalize-space(text())='ثبت سفارش']]"
        ))).click()
        print("📝 ثبت سفارش clicked")

        self.wait.until(EC.element_to_be_clickable((By.NAME, "first_name"))).send_keys("عرفان")
        self.driver.find_element(By.NAME, "last_name").send_keys("شفیعی")

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//label[.//div[normalize-space(text())='آقا']]"
        ))).click()
        self.driver.find_element(By.NAME, "national_code").send_keys("0150748094")

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//div[normalize-space(text())='ثبت']]"
        ))).click()
        print("📝 Identity submitted")

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//div[normalize-space(text())='ثبت سفارش']]"
        ))).click()

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//div[normalize-space(text())='ادامه فرآیند خرید']]"
        ))).click()
        print("➡️ ادامه فرآیند خرید clicked")

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//div[normalize-space(text())='پرداخت']]"
        ))).click()
        print("💳 پرداخت clicked")
        sleep(2)

    def run_test(self):
        self.login()
        print(f"> Buying product: {self.product_url}")

        if self.add_to_cart():
            print("✅ Added to cart.")
            self.proceed_to_payment()
            sleep(5)
            if self.driver.current_url.startswith("https://sep.shaparak.ir/OnlinePG/OnlinePG"):
                print("🎉 TEST PASSED – reached payment gateway")
            else:
                print(f"❌ TEST FAILED – landed on: {self.driver.current_url}")
        else:
            print("❌ Failed to add product to cart; aborting.")

        input("Press Enter to finish…")
        self.driver.quit()


if __name__ == "__main__":
    tester = MarketplaceCheckoutTester(
        product_url="https://marketplace-staging.dgstack.ir/product/PFFDCPA"
    )
    tester.run_test()
