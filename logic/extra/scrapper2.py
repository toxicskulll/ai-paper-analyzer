import os
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from playwright.async_api import async_playwright

# Configuration
DOWNLOAD_FOLDER = r"D:\hack\ai-paper-analyzer\downloaded_pdf"
MAX_RESULTS = 2  # Desired number of papers to download
SEARCH_PARAMS = {
    "queryText": "transformer attention",
    "sortType": "paper-citations"
}

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def build_search_url(params):
    base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?"
    query = {k: v for k, v in params.items() if v}
    return base_url + urllib.parse.urlencode(query)

def initialize_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment to run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_ieee_papers_via_rest(search_params, max_results):
    import json

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://ieeexplore.ieee.org",
        "Referer": "https://ieeexplore.ieee.org/",
        "Connection": "keep-alive"
    }

    # Step 1: Visit homepage to get cookies
    try:
        session.get("https://ieeexplore.ieee.org/", headers=headers, timeout=10)
    except Exception as e:
        print(f"⚠️ Error initializing session: {e}")

    # Step 2: Create payload
    payload = {
        "queryText": search_params.get("queryText", ""),
        "highlight": True,
        "returnType": "SEARCH",
        "matchPubs": True,
        "rowsPerPage": max_results * 2,
        "sortType": search_params.get("sortType", "relevance")
    }

    for key in ["author", "publisher", "year", "doi"]:
        if search_params.get(key):
            payload.setdefault("refinements", []).append(f"{key}:{search_params[key]}")

    try:
        res = session.post("https://ieeexplore.ieee.org/rest/search", headers=headers, json=payload, timeout=15)
        if res.status_code != 200 or not res.headers.get("Content-Type", "").startswith("application/json"):
            print(f"❌ IEEE Xplore rejected the request (status={res.status_code}, content-type={res.headers.get('Content-Type')})")
            return []

        data = res.json()
    except Exception as e:
        print(f"❌ Error parsing IEEE response: {e}")
        return []

    # Step 3: Parse papers
    papers = []
    for record in data.get("records", []):
        title = record.get("articleTitle", "Unknown Title")
        doi = record.get("doi", "")
        url = "https://ieeexplore.ieee.org" + record.get("documentLink", "")
        papers.append({"title": title, "url": url, "doi": doi})
        if len(papers) >= max_results * 3:
            break

    return papers

def download_from_scihub(identifier, title):
    scihub_url = "https://sci-hub.se/"
    try:
        response = requests.get(scihub_url + identifier, timeout=15)
        if response.status_code != 200:
            print(f"❌ Sci-Hub returned {response.status_code} for {identifier}")
            return False

        soup = BeautifulSoup(response.content, "html.parser")
        iframe = soup.find("iframe")

        print(f"🔍 Found iframe: {iframe.get('src') if iframe else 'None'}")

        if not iframe or not iframe.get("src"):
            return False

        pdf_url = iframe["src"]
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url

        pdf_response = requests.get(pdf_url, stream=True, timeout=15)
        if pdf_response.status_code == 200:
            filename = "".join(c if c.isalnum() else "_" for c in title) + ".pdf"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded: {title}")
            return True
        else:
            print(f"❌ Failed to download PDF from: {pdf_url} (status: {pdf_response.status_code})")
    except Exception as e:
        print(f"⚠️ Error downloading {title}: {e}")
    return False

def download_from_scihub_selenium(driver, identifier, title):
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    scihub_url = f"https://sci-hub.se/{identifier}"
    print(f"🌐 Opening Sci-Hub: {scihub_url}")
    
    try:
        driver.get(scihub_url)
        time.sleep(2)

        # CAPTCHA detection
        if "captcha" in driver.page_source.lower() or "i'm not a robot" in driver.page_source.lower():
            print(f"🤖 CAPTCHA detected for: {title}")
            print("👉 Please solve the CAPTCHA manually in the opened browser tab...")

        # Wait for PDF object/embed/iframe
        print("⏳ Waiting for PDF content element...")
        WebDriverWait(driver, 120).until(
            lambda d: (
                d.find_elements(By.TAG_NAME, "iframe") or
                d.find_elements(By.TAG_NAME, "embed") or
                d.find_elements(By.TAG_NAME, "object")
            )
        )

        # Try all supported PDF containers
        pdf_url = None
        for tag in ["iframe", "embed", "object"]:
            try:
                el = driver.find_element(By.TAG_NAME, tag)
                src_attr = "data" if tag == "object" else "src"
                pdf_url = el.get_attribute(src_attr)
                if pdf_url:
                    break
            except NoSuchElementException:
                continue

        if not pdf_url:
            print(f"❌ No PDF URL found in iframe/embed/object for: {title}")
            return False

        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url

        print(f"📄 PDF URL found: {pdf_url}")

        # Download
        pdf_response = requests.get(pdf_url, stream=True, timeout=20)
        if pdf_response.status_code == 200:
            filename = "".join(c if c.isalnum() else "_" for c in title) + ".pdf"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded (via Selenium): {title}")
            return True
        else:
            print(f"⚠️ Failed to download PDF from: {pdf_url} (status: {pdf_response.status_code})")
    except Exception as e:
        print(f"⚠️ Unexpected error for {title}: {e}")
    return False

async def download_pdf_playwright(doi, title):
    filepath = os.path.join(DOWNLOAD_FOLDER, "".join(c if c.isalnum() else "_" for c in title) + ".pdf")
    scihub_url = f"https://sci-hub.se/{doi}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"🌐 Opening Sci-Hub: {scihub_url}")
        await page.goto(scihub_url, wait_until="load")

        print("🤖 Solve CAPTCHA manually in browser if present (waiting 25s)...")
        await asyncio.sleep(25)

        print("⏳ Scrolling to trigger lazy loading...")
        for _ in range(25):
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(0.25)

        print(f"💾 Saving PDF to {filepath}")
        await page.pdf(path=filepath, format="A4", print_background=True)

        await browser.close()
        return True

def main():
    search_url = build_search_url(SEARCH_PARAMS)
    print(f"IEEE Xplore search URL:\n{search_url}\n")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))  # For Selenium fallback

    try:
        papers = scrape_ieee_papers_via_rest(SEARCH_PARAMS, MAX_RESULTS)
        print(f"\n✅ Scraped {len(papers)} papers from IEEE:")
        for i, paper in enumerate(papers):
            print(f"{i+1}. {paper['title']}")
            print(f"    DOI : {paper['doi']}")
            print(f"    URL : {paper['url']}\n")

        downloaded = 0
        for paper in papers:
            if downloaded >= MAX_RESULTS:
                break
            print(f"➡️  Attempting download for: {paper['title']}")
            success = download_from_scihub(paper["url"], paper["title"])

            if not success and paper["doi"]:
                print("   ⏪ Retrying with DOI...")
                success = download_from_scihub(paper["doi"], paper["title"])

            if not success:
                print("   🔄 Trying Selenium fallback...")
                success = download_from_scihub_selenium(driver, paper["doi"] or paper["url"], paper["title"])

            if not success:
                print("   🔄 Trying Playwright fallback...")
                try:
                    success = asyncio.run(download_pdf_playwright(paper["doi"] or paper["url"], paper["title"]))
                except Exception as e:
                    print(f"⚠️ Playwright error: {e}")

            if success:
                downloaded += 1
            else:
                print(f"❌ Could not download: {paper['title']}")

    finally:
        driver.quit()

    print(f"\n📦 Total papers downloaded: {downloaded} / {MAX_RESULTS}")

    
if __name__ == "__main__":
    main()
