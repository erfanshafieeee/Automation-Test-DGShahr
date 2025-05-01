import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constants import PHONE_NUMBER
from functions import get_url
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# ── CONFIG ───────────────────────────────────────────────────────────
# Directly target this product instead of scanning a category
PRODUCT_URL = "https://marketplace-staging.dgstack.ir/product/PFFDCPA"
# ── END CONFIG ────────────────────────────────────────────────────────

# Set up Chrome options
opts = Options()
opts.add_argument('--log-level=3')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])
# Allow remote origins for Chrome 135+
opts.add_argument('--remote-allow-origins=*')
# Uncomment if you want headless mode
# opts.add_argument('--headless')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)
wait = WebDriverWait(driver, 10)

def login():
    """
    Logs in using PHONE_NUMBER and OTP via the staging site.
    """
    get_url(driver, "https://marketplace-staging.dgstack.ir/shop")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    login_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[p[normalize-space(text())='ثبت‌نام'] and p[normalize-space(text())='ورود']]"
    )))
    login_btn.click()

    phone_in = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#phone")))
    phone_in.send_keys(PHONE_NUMBER)

    get_code_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[div[normalize-space(text())='دریافت کد']]"
    )))
    get_code_btn.click()
    sleep(2)

    otp_in = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#dgs-ui-kit-otp-input-0")))
    otp = input("Enter OTP code: ")
    otp_in.send_keys(otp)
    sleep(5)
    # Ensure we're back on the shop dashboard after login
    get_url(driver, "https://marketplace-staging.dgstack.ir/shop")
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    print("✅ Logged in successfully")


def add_to_cart_simple(product_url: str) -> bool:
    """
    Navigate to the given product URL, skip if variants exist,
    click Add to Cart, and confirm via modal.
    """
    get_url(driver, product_url)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    sleep(0.5)

    # Skip products requiring variant selection
    if driver.find_elements(By.CSS_SELECTOR, "select, .variant-selector, .product-options"):
        print(f"⚠️ Skipping variant-selection product: {product_url}")
        return False

    # Locate the Add to Cart button
    buttons = driver.find_elements(
        By.XPATH,
        "//button[.//div[normalize-space(text())='افزودن به سبد خرید']]"
    )
    if not buttons:
        print(f"⚠️ No add-to-cart button found: {product_url}")
        return False

    btn = buttons[0]
    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
    btn.click()

    # Wait for confirmation modal
    try:
        wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//p[normalize-space(text())='به سبد خرید اضافه شد']"
        )))
        print(f"✅ Product added: {product_url}")
        return True
    except TimeoutException:
        print(f"⚠️ No confirmation modal for: {product_url}")
        return False


def proceed_to_payment():
    """
    Opens the cart, fills identity info, and navigates through
    the purchase to reach the payment gateway.
    """
    # Open the cart
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.mgc_shopping_cart_2_line"))).click()
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    # Click 'ثبت سفارش'
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[.//div[normalize-space(text())='ثبت سفارش']]"
    ))).click()
    print("📝 ثبت سفارش clicked")

    # Fill identity form
    wait.until(EC.element_to_be_clickable((By.NAME, "first_name"))).send_keys("عرفان")
    driver.find_element(By.NAME, "last_name").send_keys("شفیعی")
    # Select 'آقا'
    male_label = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//label[.//div[normalize-space(text())='آقا']]"
    )))
    male_label.click()
    driver.find_element(By.NAME, "national_code").send_keys("0150748094")
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[.//div[normalize-space(text())='ثبت']]"
    ))).click()
    print("📝 Identity submitted")

    # Click 'ثبت سفارش' again
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[.//div[normalize-space(text())='ثبت سفارش']]"
    ))).click()

    # Continue process
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[.//div[normalize-space(text())='ادامه فرآیند خرید']]"
    ))).click()
    print("➡️ ادامه فرآیند خرید clicked")

    # Click 'پرداخت'
    wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[.//div[normalize-space(text())='پرداخت']]"
    ))).click()
    print("💳 پرداخت clicked")
    sleep(2)


def main_test():
    login()

    print(f"> Buying product: {PRODUCT_URL}")
    if add_to_cart_simple(PRODUCT_URL):
        print("✅ Added to cart.")
        proceed_to_payment()
        sleep(5)
        current = driver.current_url
        if current.startswith("https://sep.shaparak.ir/OnlinePG/OnlinePG"):
            print("🎉 TEST PASSED – reached payment gateway")
        else:
            print(f"❌ TEST FAILED – landed on: {current}")
    else:
        print("❌ Failed to add product to cart; aborting.")

    input("Press Enter to finish…")
    driver.quit()


if __name__ == "__main__":
    main_test()
