import json
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ---- CONFIG ----
PRODUCTS_FILE = "products.json"
SCRAPE_DELAY = 10 
MAX_PRODUCTS = 20

class ProductScraper:
    def __init__(self):
        # Browser setup
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.products = []

    def parse_laptop_details(self, title):
        """Extract detailed specs from the product title using Regex"""
        specs = {
            "Brand": "N/A", "Model": "N/A", "CPU": "N/A",
            "RAM": "N/A", "Storage": "N/A", "GPU": "N/A", "OS": "N/A"
        }
        
        # 1. Identify Brand
        brands = ["ASUS", "HP", "DELL", "LENOVO", "MSI", "ACER", "APPLE", "GIGABYTE"]
        for b in brands:
            if b.lower() in title.lower():
                specs["Brand"] = b
                break

        # 2. Extract RAM (e.g., 16GB)
        ram_match = re.search(r'(\d+\s?GB)', title, re.IGNORECASE)
        if ram_match: specs["RAM"] = ram_match.group(1)

        # 3. Extract Storage (e.g., 512GB SSD)
        storage_match = re.search(r'(\d+\s?(GB|TB)\s?SSD)', title, re.IGNORECASE)
        if storage_match: specs["Storage"] = storage_match.group(1)

        # 4. Extract CPU (Intel/AMD)
        cpu_match = re.search(r'(AMD Ryzen™? \d \d+\w+|Intel Core™? i\d-\d+\w+)', title, re.IGNORECASE)
        if cpu_match: specs["CPU"] = cpu_match.group(1)

        # 5. Extract GPU (RTX/GTX/Radeon)
        gpu_match = re.search(r'(RTX™?\s?\d+\s?\d?GB?|GTX\s?\d+|Radeon\s?\w+)', title, re.IGNORECASE)
        if gpu_match: specs["GPU"] = gpu_match.group(1)

        # 6. Extract OS
        if "Win" in title or "Windows" in title: 
            specs["OS"] = "Windows 11" if "11" in title else "Windows"
        elif "Mac" in title: 
            specs["OS"] = "macOS"

        # 7. Guess Model name
        words = title.split()
        if len(words) > 2:
            specs["Model"] = " ".join(words[1:4])

        return specs

    def open_page(self, url):
        print(f"🚀 Opening Amazon: {url}")
        self.driver.get(url)
        time.sleep(SCRAPE_DELAY + random.uniform(1, 3))

    def scroll_page(self):
        """Scroll down to trigger lazy-loading of items"""
        print("📜 Scrolling to load items...")
        for fraction in [3, 1.5, 1]:
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/{fraction});")
            time.sleep(1.5)

    def extract_product(self, item):
        """Find title, price, and parse specs from a single search result"""
        try:
            title = "N/A"
            title_selectors = ["h2 a span", "span.a-size-base-plus.a-color-base.a-text-normal", "h2 span"]
            for sel in title_selectors:
                try:
                    element = item.find_element(By.CSS_SELECTOR, sel)
                    title = element.text.strip()
                    if title: break
                except: continue

            if not title or title == "N/A": return None

            # Get Price
            price = "N/A"
            try:
                p_whole = item.find_element(By.CSS_SELECTOR, ".a-price-whole").text
                price = f"{p_whole.replace(',', '').replace('\n', '').strip()} EGP"
            except:
                try: price = item.find_element(By.CSS_SELECTOR, ".a-offscreen").get_attribute("innerText")
                except: pass

            specs = self.parse_laptop_details(title)

            return {
                "Full Name": title,
                "Price": price,
                **specs
            }
        except:
            return None

    def scrape_page(self):
        """Loop through all product containers found on page"""
        items = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')
        print(f"🔍 Found {len(items)} items. Starting extraction...")
        
        for item in items:
            if len(self.products) >= MAX_PRODUCTS: break
            product = self.extract_product(item)
            if product:
                self.products.append(product)
                print(f"    [{len(self.products)}] {product['Brand']} {product['Model']} | {product['Price']}")

    def save_products(self):
        if not self.products:
            print("⚠️ No products found.")
            return
            
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.products, f, indent=4, ensure_ascii=False)
        print(f"\n🎉 Saved {len(self.products)} products to '{PRODUCTS_FILE}'.")

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    target_url = "https://www.amazon.eg/s?rh=n%3A21832907031%2Cp_n_feature_two_browse-bin%3A27370241031&language=en"
    scraper = ProductScraper()
    try:
        scraper.open_page(target_url)
        scraper.scroll_page()
        scraper.scrape_page()
        scraper.save_products()
    except Exception as e:
        print(f" Error: {e}")
    finally:
        scraper.close()