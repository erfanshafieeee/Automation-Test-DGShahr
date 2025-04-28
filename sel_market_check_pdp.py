from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from constants import PHONE_NUMBER
from functions import get_url
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random

# number of products to test, adjust as needed
TEST_COUNT = 20

# Configure ChromeOptions to reduce logging noise
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Initialize WebDriver
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# 1) Navigate to the shop page and log in
get_url(driver, "https://marketplace-staging.dgstack.ir/shop")
sleep(3)

login_button = driver.find_element(
    By.XPATH,
    "//button[.//div[contains(@class,'mgc_user_2_line')]]"
)
login_button.click()

phone_input = driver.find_element(By.XPATH, "//input[@id='phone']")
phone_input.send_keys(PHONE_NUMBER)

phone_button = driver.find_element(
    By.CSS_SELECTOR,
    "button.dgs-ui-kit-bg-primary-500.button-medium-icon"
)
phone_button.click()
sleep(3)

otp_input = driver.find_element(By.XPATH, "//input[@id='dgs-ui-kit-otp-input-0']")
otp_code = input("Enter OTP code: ")
otp_input.send_keys(otp_code)

# Return to shop page and wait for full load
get_url(driver, "https://marketplace-staging.dgstack.ir/shop")
WebDriverWait(driver, 10).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)

# 2) Discover product URLs by scrolling the shop page
product_links = set()
last_count = 0

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)
    anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/product/"]')
    for a in anchors:
        product_links.add(a.get_attribute('href'))
    # stop when we have enough links or no new ones
    if len(product_links) >= TEST_COUNT or len(product_links) == last_count:
        break
    last_count = len(product_links)

# pick up to TEST_COUNT random product URLs
to_test = random.sample(list(product_links), min(TEST_COUNT, len(product_links)))
total_urls = len(to_test)

# Initialize statistics
ok_urls = 0
failed_image_pages = []
unreachable_pages = []

total_images = 0
loaded_images = 0
failed_images = 0
failure_details = []  # list of (product_url, image_src)

# 3) Iterate over each random product URL and check images
for url in to_test:
    try:
        get_url(driver, url)
    except Exception:
        unreachable_pages.append(url)
        print(f"⚠️ Page unreachable: {url}")
        continue

    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)

    images = driver.find_elements(By.TAG_NAME, "img")
    page_failed = False

    for img in images:
        src = img.get_attribute('src')
        # skip trustseal/enamad logo images
        if "trustseal.enamad.ir" in src:
            continue

        total_images += 1
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", img
        )

        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script(
                    "return arguments[0].complete && arguments[0].naturalWidth > 0;",
                    img
                )
            )
            loaded_images += 1
        except:
            failed_images += 1
            page_failed = True
            failure_details.append((url, src))
            print(f"⚠️ Failed to load image on {url}: {src}")

    if page_failed:
        failed_image_pages.append(url)
    else:
        ok_urls += 1
        print(f"✅ All images on {url} loaded successfully")

# 4) Print summary statistics
print("\n--- SUMMARY ---")
print(f"Requested tests:                {total_urls}")
print(f"✔️  OK pages:                   {ok_urls} ({ok_urls/total_urls*100:.1f}%)")
print(f"❌  Pages w/ image failures:    {len(failed_image_pages)} ({len(failed_image_pages)/total_urls*100:.1f}%)")
print(f"⚠️  Unreachable pages:          {len(unreachable_pages)} ({len(unreachable_pages)/total_urls*100:.1f}%)\n")

print(f"Total images checked:           {total_images}")
print(f"✅  Loaded images:              {loaded_images} ({loaded_images/total_images*100:.1f}%)")
print(f"⚠️  Failed images:              {failed_images} ({failed_images/total_images*100:.1f}%)\n")

if failure_details:
    print("Images that failed to load:")
    for product_url, img_src in failure_details:
        print(f" - {product_url} -> {img_src}")

# 5) Keep the browser open for manual inspection if needed
input("Press Enter to exit and close the browser...")
driver.quit()
