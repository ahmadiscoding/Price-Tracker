import openpyxl
from datetime import datetime
import os
from playwright.sync_api import sync_playwright

# Add URLs here 
PRODUCTS = [
    {
        "name": "AMD Ryzen™ 5 9600X 6-Core, 12-Thread Unlocked Desktop Processor",
        "url": "https://www.amazon.com/AMD-RyzenTM-9600X-12-Thread-Processor/dp/B0D6NN6TM7/?_encoding=UTF8&pd_rd_w=RBZG5&content-id=amzn1.sym.10f16e90-d621-4a53-9c61-544e5c741acc&pf_rd_p=10f16e90-d621-4a53-9c61-544e5c741acc&pf_rd_r=8XS48P4K3RYWRC8DS24F&pd_rd_wg=zw2Nq&pd_rd_r=2b018178-bebc-4087-935e-e75306779a41&ref_=pd_hp_d_btf_exports_top_sellers_unrec&th=1"
    },
    {
        "name": "Samsung Galaxy A56 12/256GB - PTA APPROVED",
        "url" : "https://www.daraz.pk/products/samsung-galaxy-a56-12256gb-pta-approved-i781674228-s3615764678.html?scm=1007.51610.379274.0&pvid=d566874d-978d-473d-8fa6-ce137ccabebe&search=flashsale&spm=a2a0e.tm80335142.FlashSale.d_781674228"
    },

    

    # We can add more products like this:
]

OUTPUT_FILE = "price_history.xlsx"

# -----------------------------------------------------------------


def get_daraz_price(page, url):
    """Extract realtime discounted price from Daraz using Playwright to render JS"""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        
        # Wait for the price elements to be visible
        page.wait_for_selector(".pdp-price", timeout=10000)
        price_elem = page.locator(".pdp-price").first
        if price_elem:
            return price_elem.inner_text().strip()

        return "Price not found"

    except Exception as e:
        return f"Error: {e}"


def get_amazon_price(page, url):
    """Extract price from Amazon using Playwright"""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        
        # Amazon prices are often in .a-price .a-offscreen
        page.wait_for_selector(".a-price .a-offscreen", timeout=10000)
        price_text = page.locator(".a-price .a-offscreen").first.text_content()
        
        if price_text:
            return price_text.strip()

        return "Price not found"

    except Exception as e:
        return f"Error: {e}"



def save_to_excel(name, url, price):
    """Save result to Excel with product name column."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if os.path.exists(OUTPUT_FILE):
        wb = openpyxl.load_workbook(OUTPUT_FILE)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Timestamp", "Product", "Price", "URL"])

    ws.append([now, name, price, url])
    wb.save(OUTPUT_FILE)
    print(f"  Saved -> {name}: {price} at {now}")


def main():
    print("\n=== Price Tracker ===\n")
    
    with sync_playwright() as p:
        # Launch once for all items to save time
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for p_info in PRODUCTS:
            print(f"Checking: {p_info['name']}...")
            url = p_info["url"]
            if "amazon." in url:
                price = get_amazon_price(page, url)
            else:
                price = get_daraz_price(page, url)
            
            print(f"  Result: {price}")
            save_to_excel(p_info["name"], url, price)

            
        browser.close()
        
    print(f"\nDone! Open {OUTPUT_FILE} to see results.")


if __name__ == "__main__":
    main()