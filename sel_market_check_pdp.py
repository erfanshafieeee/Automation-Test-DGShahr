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

# ── CONFIG ───────────────────────────────────────────────────────────
# the 10 category URLs you provided:
CATEGORY_URLS = [
    "https://marketplace-staging.dgstack.ir/plp/category/2240",
    "https://marketplace-staging.dgstack.ir/plp/category/2236",
    "https://marketplace-staging.dgstack.ir/plp?category_id=2316",
    "https://marketplace-staging.dgstack.ir/plp/category/2209",
    "https://marketplace-staging.dgstack.ir/plp/category/2763",
    "https://marketplace-staging.dgstack.ir/plp?category_id=2482",
    "https://marketplace-staging.dgstack.ir/plp?category_id=2451",
    "https://marketplace-staging.dgstack.ir/plp/category/2367",
    "https://marketplace-staging.dgstack.ir/plp/category/2478",
]
PRODUCTS_PER_CATEGORY = 2   # how many random products to test per category
# ── END CONFIG ────────────────────────────────────────────────────────

# initialize Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
wait = WebDriverWait(driver, 10)

# ── 1) LOGIN ─────────────────────────────────────────────────────────
get_url(driver, "https://marketplace-staging.dgstack.ir/shop")
sleep(2)

# open login modal
driver.find_element(
    By.XPATH,
    "//button[.//div[contains(@class,'mgc_user_2_line')]]"
).click()

# enter phone number and request OTP
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#phone")))\
    .send_keys(PHONE_NUMBER)
driver.find_element(
    By.CSS_SELECTOR,
    "button.dgs-ui-kit-bg-primary-500.button-medium-icon"
).click()
sleep(2)

# enter OTP code
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#dgs-ui-kit-otp-input-0")))\
    .send_keys(input("Enter OTP code: "))

# ensure shop page is loaded
get_url(driver, "https://marketplace-staging.dgstack.ir/shop")
wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

# ── 2) ITERATE CATEGORIES & TEST PRODUCTS ────────────────────────────
total_categories = len(CATEGORY_URLS)
total_tested = 0
ok_products = 0
failed_products = []

total_images = 0
loaded_images = 0
failed_images = 0
failure_details = []  # list of (product_url, image_src)

for cat_url in CATEGORY_URLS:
    # navigate to category URL
    get_url(driver, cat_url)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    sleep(1)

    # scroll to bottom to load all products
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)

    # collect all product links on this category page
    anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/product/']")
    product_links = []
    for a in anchors:
        href = a.get_attribute('href')
        if href and href not in product_links:
            product_links.append(href)

    # pick random products from this category
    to_test = random.sample(product_links, min(PRODUCTS_PER_CATEGORY, len(product_links)))
    print(f"🔖 Category: {cat_url} — testing {len(to_test)} products")

    for url in to_test:
        total_tested += 1
        try:
            get_url(driver, url)
        except:
            failed_products.append((url, "unreachable"))
            continue

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        # trigger lazy-load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.5)

        imgs = driver.find_elements(By.TAG_NAME, "img")
        product_ok = True

        for img in imgs:
            src = img.get_attribute('src') or ""
            # skip trustseal logo
            if "trustseal.enamad.ir" in src:
                continue

            total_images += 1
            # scroll image into view
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)
            try:
                wait.until(lambda d: d.execute_script(
                    "return arguments[0].complete && arguments[0].naturalWidth > 0;", img
                ))
                loaded_images += 1
            except:
                failed_images += 1
                product_ok = False
                failure_details.append((url, src))
                print(f"⚠️ Failed image: {src} on {url}")

        if product_ok:
            ok_products += 1
            print(f"✅ Product OK: {url}")
        else:
            failed_products.append((url, "some images failed"))

# ── 3) PRINT SUMMARY ──────────────────────────────────────────────────
print("\n--- SUMMARY ---")
print(f"Categories scanned:       {total_categories}")
print(f"Products tested:          {total_tested}")
if total_tested:
    print(f"✔️ Products all-images-OK: {ok_products} ({ok_products/total_tested*100:.1f}%)")
    print(f"❌ Products with issues:   {len(failed_products)} ({len(failed_products)/total_tested*100:.1f}%)")
else:
    print("⚠️ No products were tested — check CATEGORY_URLS")

print(f"\nTotal images checked:     {total_images}")
if total_images:
    print(f"✅ Loaded images:         {loaded_images} ({loaded_images/total_images*100:.1f}%)")
    print(f"⚠️ Failed images:         {failed_images} ({failed_images/total_images*100:.1f}%)")
else:
    print("⚠️ No images were found — check selectors")

if failure_details:
    print("\nFailed image details:")
    for prod, src in failure_details:
        print(f" - {src} on {prod}")

# ── 4) KEEP BROWSER OPEN FOR INSPECTION ───────────────────────────────
input("\nPress Enter to exit and close browser...")
driver.quit()
