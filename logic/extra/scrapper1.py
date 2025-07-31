import requests
import os
import asyncio
from playwright.async_api import async_playwright
import json
import streamlit as st

DOWNLOAD_FOLDER = r"D:\hack\ai-paper-analyzer\downloaded_pdf"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

SEARCH_PARAMS = {
    "queryText": "transformer attention",
    "author": "",
    "publisher": "",
    "year": "",
    "doi": "",
    "sortType": "paper-citations"
}
MAX_RESULTS = 2

# === Step 1: IEEE REST Search ===
def scrape_ieee_papers_via_rest(search_params, max_results):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://ieeexplore.ieee.org/",
        "Origin": "https://ieeexplore.ieee.org",
        "Content-Type": "application/json"
    }

    session.get("https://ieeexplore.ieee.org/", headers=headers)

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
    except Exception as e:
        print(f"❌ IEEE POST request failed: {e}")
        return []

    if res.status_code != 200 or not res.headers.get("Content-Type", "").startswith("application/json"):
        print(f"❌ IEEE API error — Status: {res.status_code} | Reason: {res.reason}")
        print("Response Text:\n", res.text)
        return []

    try:
        data = res.json()
    except json.JSONDecodeError as e:
        print(f"❌ Failed to decode JSON: {e}")
        print("Raw response:\n", res.text)
        return []

    papers = []
    for record in data.get("records", []):
        title = record.get("articleTitle", "Unknown Title")
        doi = record.get("doi", "")
        papers.append({"title": title, "doi": doi})
        if len(papers) >= max_results:
            break

    return papers

# === Step 2: Playwright-based PDF Downloader ===
async def download_from_scihub(doi_or_url, title):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        scihub_url = f"https://sci-hub.se/{doi_or_url}"
        print(f"🌐 Opening Sci-Hub: {scihub_url}")
        await page.goto(scihub_url, wait_until="load")

        print("🤖 If CAPTCHA appears, please solve it manually. Waiting 20s...")
        await asyncio.sleep(20)

        for _ in range(30):
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(0.3)

        filename = "".join(c if c.isalnum() else "_" for c in title) + ".pdf"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        await page.pdf(path=filepath, format="A4", print_background=True)

        print(f"✅ Saved PDF: {filepath}")
        await browser.close()

# === Step 3: Download Multiple Papers ===
def download_papers_with_playwright(paper_list):
    for paper in paper_list:
        title = paper["title"]
        doi = paper["doi"]
        if not doi:
            print(f"⚠️ Skipping '{title}' — no DOI found.")
            continue
        asyncio.run(download_from_scihub(doi, title))

# === MAIN ===
if __name__ == "__main__":
    print("📡 Fetching papers from IEEE...")
    papers = scrape_ieee_papers_via_rest(SEARCH_PARAMS, MAX_RESULTS)
    print(f"✅ Found {len(papers)} papers.\n")

    for idx, p in enumerate(papers, 1):
        print(f"{idx}. {p['title']} — DOI: {p['doi']}")

    print("\n📥 Starting downloads from Sci-Hub...")
    download_papers_with_playwright(papers)
    print("✅ All downloads completed.")