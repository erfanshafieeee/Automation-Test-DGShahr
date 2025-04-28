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
opts = Options()
opts.add_argument('--log-level=3')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)
wait = WebDriverWait(driver, 10)

# # ── 1) LOGIN ─────────────────────────────────────────────────────────
# get_url(driver, "https://marketplace-staging.dgstack.ir/shop")
# sleep(2)

# # open login modal
# driver.find_element(
#     By.XPATH,
#     "//button[.//div[contains(@class,'mgc_user_2_line')]]"
# ).click()

# # enter phone & request OTP
# wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#phone")))\
#     .send_keys(PHONE_NUMBER)
# driver.find_element(
#     By.CSS_SELECTOR,
#     "button.dgs-ui-kit-bg-primary-500.button-medium-icon"
# ).click()
# sleep(2)

# # enter OTP
# wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#dgs-ui-kit-otp-input-0")))\
#     .send_keys(input("Enter OTP code: "))

# ensure shop loaded
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
# now record tuples of (category, product_url, img_src)
failure_details = []

for cat_url in CATEGORY_URLS:
    # navigate to category
    get_url(driver, cat_url)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    sleep(1)

    # infinite scroll to load all product links
    product_links = set()
    prev_count = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/product/']")
        for a in anchors:
            href = a.get_attribute('href')
            if href:
                product_links.add(href)
        if len(product_links) == prev_count:
            break
        prev_count = len(product_links)

    product_links = list(product_links)
    to_test = random.sample(product_links, min(PRODUCTS_PER_CATEGORY, len(product_links)))
    print(f"🔖 Category {cat_url} → found {len(product_links)} products, testing {len(to_test)}")

    for url in to_test:
        total_tested += 1
        try:
            get_url(driver, url)
        except:
            failed_products.append((cat_url, url, "unreachable"))
            continue

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.5)

        imgs = driver.find_elements(By.TAG_NAME, "img")
        product_ok = True

        for img in imgs:
            src = img.get_attribute('src') or ""
            if "trustseal.enamad.ir" in src:
                continue

            total_images += 1
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)
            try:
                wait.until(lambda d: d.execute_script(
                    "return arguments[0].complete && arguments[0].naturalWidth > 0;", img
                ))
                loaded_images += 1
            except:
                failed_images += 1
                product_ok = False
                # record category, product and src
                failure_details.append((cat_url, url, src))
                print(f"⚠️ Failed image in category [{cat_url}], product [{url}]: {src}")

        if product_ok:
            ok_products += 1
            print(f"✅ Product OK: {url}")
        else:
            failed_products.append((cat_url, url, "images failed"))

# ── 3) PRINT SUMMARY ──────────────────────────────────────────────────
print("\n--- SUMMARY ---")
print(f"Categories scanned:       {total_categories}")
print(f"Products tested:          {total_tested}")
if total_tested:
    print(f"✔️ Products OK:           {ok_products} ({ok_products/total_tested*100:.1f}%)")
    print(f"❌ Products issues:       {len(failed_products)} ({len(failed_products)/total_tested*100:.1f}%)")
else:
    print("⚠️ No products were tested — check CATEGORY_URLS or login state")

print(f"\nTotal images checked:     {total_images}")
if total_images:
    print(f"✅ Loaded images:         {loaded_images} ({loaded_images/total_images*100:.1f}%)")
    print(f"⚠️ Failed images:         {failed_images} ({failed_images/total_images*100:.1f}%)")
else:
    print("⚠️ No images were found — check selectors")

if failure_details:
    print("\nDetailed failures:")
    for category, prod, src in failure_details:
        print(f" - Category [{category}] → Product [{prod}] → Image [{src}]")

# ── 4) KEEP BROWSER OPEN FOR INSPECTION ───────────────────────────────
input("\nPress Enter to exit and close browser...")
driver.quit()
