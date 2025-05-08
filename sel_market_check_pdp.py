import random
import requests
from time import sleep
from typing import List, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from functions import get_url

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
PRODUCTS_PER_CATEGORY = 2

# Webhook URL of deployed Apps Script (must end in /exec)
WEBHOOK_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbykd4NnH0ouuhOsrQuye4kJUyGFAjwgObwRyzDHYe-GtU0GM4LcKVWSxf9VRvmbKXK06w/exec"
)
# ── END CONFIG ────────────────────────────────────────────────────────


class MarketplaceTester:
    """
    Automates checking product image loads across categories and
    reports failures via a webhook to Google Sheets.
    """

    def __init__(self):
        self.driver = self._init_driver()
        self.wait = WebDriverWait(self.driver, 10)

        # Counters
        self.total_categories = len(CATEGORY_URLS)
        self.total_tested = 0
        self.ok_products = 0
        self.failed_products: List[Tuple[str, str, str]] = []
        self.total_images = 0
        self.loaded_images = 0
        self.failed_images = 0
        self.failure_details: List[Tuple[str, str, str]] = []

    @staticmethod
    def _init_driver() -> webdriver.Chrome:
        """Initialize Chrome WebDriver with minimal logging."""
        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

    def _collect_product_links(self, category_url: str) -> List[str]:
        """
        Loads all paginated product pages in a category and collects product URLs.
        """
        links = set()
        page = 1
    
        while True:
            # Append page parameter
            if "?" in category_url:
                url = f"{category_url}&p={page}"
            else:
                url = f"{category_url}?p={page}"
    
            get_url(self.driver, url)
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            sleep(1)
    
            anchors = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/product/']")
            new_links = [a.get_attribute("href") for a in anchors if a.get_attribute("href")]
            print(f"📄 Page {page}: Found {len(new_links)} products")
    
            before_count = len(links)
            links.update(new_links)
    
            if len(links) == before_count:
                break  # No new products → assume end of pagination
            
            page += 1
    
        return list(links)
    
    
    def _test_product(self, category_url: str, product_url: str):
        """
        Opens a product page, scrolls to load images, and records any failures.
        """
        self.total_tested += 1
        try:
            get_url(self.driver, product_url)
        except Exception:
            self.failed_products.append((category_url, product_url, "unreachable"))
            return

        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.5)

        imgs = self.driver.find_elements(By.TAG_NAME, "img")
        product_ok = True

        for img in imgs:
            src = img.get_attribute("src") or ""
            if "trustseal.enamad.ir" in src:
                continue

            self.total_images += 1
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)

            try:
                self.wait.until(lambda d: d.execute_script(
                    "return arguments[0].complete && arguments[0].naturalWidth > 0;", img
                ))
                self.loaded_images += 1
            except Exception:
                self.failed_images += 1
                product_ok = False
                self.failure_details.append((category_url, product_url, src))
                print(f"⚠️ Failed image in category [{category_url}], product [{product_url}]: {src}")

        if product_ok:
            self.ok_products += 1
            print(f"✅ Product OK: {product_url}")
        else:
            self.failed_products.append((category_url, product_url, "images failed"))

    def _sync_failures_to_sheet(self):
        """
        Posts any collected failures to the Google Sheets webhook.
        """
        if not self.failure_details:
            return

        payload = {
            "failures": [
                {"category": c, "product": p, "image": i}
                for c, p, i in self.failure_details
            ]
        }

        try:
            resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            print("🔗 Webhook response:", resp.status_code, resp.text)
            if resp.status_code != 200:
                print(f"‼️ Webhook error: {resp.status_code} {resp.text}")
        except Exception as e:
            print("‼️ Error posting to webhook:", e)

    def run(self):
        """
        Main entry point: iterates categories, tests products,
        synchronizes failures, and prints a summary.
        """
        # Ensure the shop page is loaded
        get_url(self.driver, "https://marketplace-staging.dgstack.ir/shop")
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Iterate all categories
        for cat_url in CATEGORY_URLS:
            product_links = self._collect_product_links(cat_url)
            to_test = random.sample(product_links, min(PRODUCTS_PER_CATEGORY, len(product_links)))
            print(f"🔖 Category {cat_url} → found {len(product_links)} products, testing {len(to_test)}")

            for prod_url in to_test:
                self._test_product(cat_url, prod_url)

        # Report failures
        self._sync_failures_to_sheet()

        # Print summary
        print("\n--- SUMMARY ---")
        print(f"Categories scanned:       {self.total_categories}")
        print(f"Products tested:          {self.total_tested}")
        if self.total_tested:
            print(f"✔️ Products OK:           {self.ok_products} ({self.ok_products/self.total_tested*100:.1f}%)")
            print(f"❌ Products issues:       {len(self.failed_products)} "
                  f"({len(self.failed_products)/self.total_tested*100:.1f}%)")
        else:
            print("⚠️ No products were tested — check CATEGORY_URLS or login state")

        print(f"\nTotal images checked:     {self.total_images}")
        if self.total_images:
            print(f"✅ Loaded images:         {self.loaded_images} "
                  f"({self.loaded_images/self.total_images*100:.1f}%)")
            print(f"⚠️ Failed images:         {self.failed_images} "
                  f"({self.failed_images/self.total_images*100:.1f}%)")
        else:
            print("⚠️ No images were found — check selectors")

        if self.failure_details:
            print("\nDetailed failures:")
            for c, p, i in self.failure_details:
                print(f" - Category [{c}] → Product [{p}] → Image [{i}]")

        input("\nPress Enter to exit and close browser...")
        self.driver.quit()


if __name__ == "__main__":
    tester = MarketplaceTester()
    tester.run()
