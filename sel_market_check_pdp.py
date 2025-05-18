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


class WebDriverFactory:
    @staticmethod
    def create_driver() -> webdriver.Chrome:
        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )


class ProductCollector:
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def collect_links(self, category_url: str, mode: str, max_pages: int = 10) -> List[str]:
        if mode == "fast":
            return self._collect_from_fast(category_url)
        elif mode == "random":
            return self._collect_from_random(category_url, max_pages)
        elif mode == "full":
            return self._collect_from_full(category_url)
        raise ValueError(f"Unknown mode: {mode}")

    def _collect_from_fast(self, url: str) -> List[str]:
        self._load_page(url)
        return self._scroll_and_collect_links()

    def _collect_from_random(self, url: str, max_pages: int) -> List[str]:
        total_pages = self._get_total_pages(url)
        pages_to_check = random.sample(range(1, total_pages + 1), min(max_pages, total_pages))
        links = set()
        for page in pages_to_check:
            page_url = f"{url}&p={page}" if "?" in url else f"{url}?p={page}"
            self._load_page(page_url)
            links.update(self._extract_links())
        return list(links)

    def _collect_from_full(self, url: str) -> List[str]:
        page = 1
        links = set()
        while True:
            page_url = f"{url}&p={page}" if "?" in url else f"{url}?p={page}"
            self._load_page(page_url)
            new_links = self._extract_links()
            if not new_links:
                break
            links.update(new_links)
            page += 1
        return list(links)

    def _load_page(self, url: str):
        self.driver.get(url)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        sleep(1)

    def _scroll_and_collect_links(self) -> List[str]:
        links = set()
        prev_count = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)
            anchors = self._extract_links()
            links.update(anchors)
            if len(links) == prev_count:
                break
            prev_count = len(links)
        return list(links)

    def _extract_links(self) -> List[str]:
        anchors = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/product/']")
        return [a.get_attribute("href") for a in anchors if a.get_attribute("href")]

    def _get_total_pages(self, url: str) -> int:
        page = 1
        while True:
            page_url = f"{url}&p={page}" if "?" in url else f"{url}?p={page}"
            self._load_page(page_url)
            if not self._extract_links():
                break
            page += 1
        return page - 1


class FailureReporter:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def report(self, failures: List[Tuple[str, str, str]]):
        if not failures:
            return
        payload = {"failures": [{"category": c, "product": p, "image": i} for c, p, i in failures]}
        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            print("🔗 Webhook response:", resp.status_code, resp.text)
        except Exception as e:
            print("‼️ Error posting to webhook:", e)


class MarketplaceTester:
    CATEGORY_URLS = [
        "https://marketplace-staging.dgstack.ir/plp/category/2240",
        "https://marketplace-staging.dgstack.ir/plp/category/2236",
        "https://marketplace-staging.dgstack.ir/plp?category_id=2316",
        "https://marketplace-staging.dgstack.ir/plp/category/2209",
        "https://marketplace-staging.dgstack.ir/plp/category/2763",
        "https://marketplace-staging.dgstack.ir/plp?category_id=2482",
        "https://marketplace-staging.dgstack.ir/plp?category_id=2451",
        "https://marketplace-staging.dgstack.ir/plp/category/2367",
        "https://marketplace-staging.dgstack.ir/plp/category/2478"
    ]
    PRODUCTS_PER_CATEGORY = 2
    CHECK_MODE = "fast"
    WEBHOOK_URL = "https://script.google.com/macros/s/.../exec"

    def __init__(self):
        self.driver = WebDriverFactory.create_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.collector = ProductCollector(self.driver, self.wait)
        self.reporter = FailureReporter(self.WEBHOOK_URL)

        self.ok_products = 0
        self.failed_products = []
        self.failure_details = []
        self.total_images = 0
        self.loaded_images = 0

    def run(self):
        get_url(self.driver, "https://marketplace-staging.dgstack.ir/shop")
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        for cat_url in self.CATEGORY_URLS:
            links = self.collector.collect_links(cat_url, self.CHECK_MODE)
            to_test = random.sample(links, min(self.PRODUCTS_PER_CATEGORY, len(links)))
            for prod_url in to_test:
                self._test_product(cat_url, prod_url)

        self.reporter.report(self.failure_details)
        self._print_summary()
        input("\nPress Enter to exit and close browser...")
        self.driver.quit()

    def _test_product(self, category_url: str, product_url: str):
        try:
            get_url(self.driver, product_url)
        except Exception:
            self.failed_products.append((category_url, product_url, "unreachable"))
            return

        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.5)

        product_ok = True
        imgs = self.driver.find_elements(By.TAG_NAME, "img")

        for img in imgs:
            src = img.get_attribute("src") or ""
            if "trustseal.enamad.ir" in src:
                continue

            self.total_images += 1
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)

            try:
                self.wait.until(lambda d: d.execute_script("return arguments[0].complete && arguments[0].naturalWidth > 0;", img))
                self.loaded_images += 1
            except Exception:
                product_ok = False
                self.failure_details.append((category_url, product_url, src))

        if product_ok:
            self.ok_products += 1
        else:
            self.failed_products.append((category_url, product_url, "images failed"))

    def _print_summary(self):
        total_tested = self.ok_products + len(self.failed_products)
        print("\n--- SUMMARY ---")
        print(f"Products tested: {total_tested}")
        print(f"✔️ OK: {self.ok_products}")
        print(f"❌ Failed: {len(self.failed_products)}")
        print(f"Images checked: {self.total_images}, Loaded: {self.loaded_images}, Failed: {self.total_images - self.loaded_images}")


if __name__ == "__main__":
    MarketplaceTester().run()