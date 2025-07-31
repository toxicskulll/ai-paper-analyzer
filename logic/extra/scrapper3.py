import os
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import logging
from typing import List, Dict, Optional
import random
from fake_useragent import UserAgent

# Enhanced Configuration
DOWNLOAD_FOLDER = r"D:\hack\ai-paper-analyzer\downloaded_pdf"
MAX_RESULTS = 5
SEARCH_PARAMS = {
    "queryText": "transformer attention",
    "sortType": "paper-citations"
}

# Legitimate paper sources (no paywalls)
OPEN_ACCESS_SOURCES = [
    "https://arxiv.org/",
    "https://www.biorxiv.org/",
    "https://www.medrxiv.org/",
    "https://peerj.com/",
    "https://www.frontiersin.org/",
    "https://journals.plos.org/"
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class EnhancedPaperScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.driver = None
        
    def get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to appear more human-like"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    def initialize_driver(self) -> webdriver.Chrome:
        """Initialize Chrome driver with enhanced options"""
        options = webdriver.ChromeOptions()
        
        # Anti-detection measures
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f"--user-agent={self.ua.random}")
        
        # Performance optimizations
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        
        # Execute script to hide webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def scrape_ieee_papers(self, search_params: Dict, max_results: int) -> List[Dict]:
        """Enhanced IEEE paper scraping with better error handling"""
        papers = []
        headers = self.get_random_headers()
        headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://ieeexplore.ieee.org",
            "Referer": "https://ieeexplore.ieee.org/",
        })
        
        try:
            # Initialize session
            self.session.get("https://ieeexplore.ieee.org/", headers=headers, timeout=10)
            time.sleep(random.uniform(1, 3))  # Random delay
            
            # Prepare search payload
            payload = {
                "queryText": search_params.get("queryText", ""),
                "highlight": True,
                "returnType": "SEARCH",
                "matchPubs": True,
                "rowsPerPage": max_results * 2,
                "sortType": search_params.get("sortType", "relevance")
            }
            
            response = self.session.post(
                "https://ieeexplore.ieee.org/rest/search", 
                headers=headers, 
                json=payload, 
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for record in data.get("records", []):
                    paper = {
                        "title": record.get("articleTitle", "Unknown Title"),
                        "doi": record.get("doi", ""),
                        "url": "https://ieeexplore.ieee.org" + record.get("documentLink", ""),
                        "authors": record.get("authors", {}).get("authors", []),
                        "year": record.get("publicationYear", ""),
                        "abstract": record.get("abstract", ""),
                        "source": "IEEE"
                    }
                    papers.append(paper)
                    if len(papers) >= max_results:
                        break
                        
        except Exception as e:
            logger.error(f"Error scraping IEEE papers: {e}")
            
        return papers
    
    def scrape_arxiv_papers(self, query: str, max_results: int) -> List[Dict]:
        """Scrape papers from arXiv (open access)"""
        papers = []
        base_url = "http://export.arxiv.org/api/query"
        
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "xml")
                entries = soup.find_all("entry")
                
                for entry in entries:
                    paper = {
                        "title": entry.find("title").text.strip(),
                        "doi": "",
                        "url": entry.find("id").text.strip(),
                        "authors": [author.find("name").text for author in entry.find_all("author")],
                        "year": entry.find("published").text[:4],
                        "abstract": entry.find("summary").text.strip(),
                        "source": "arXiv",
                        "pdf_url": entry.find("id").text.replace("abs", "pdf") + ".pdf"
                    }
                    papers.append(paper)
                    
        except Exception as e:
            logger.error(f"Error scraping arXiv papers: {e}")
            
        return papers
    
    def download_pdf_direct(self, url: str, title: str) -> bool:
        """Download PDF directly when available"""
        try:
            headers = self.get_random_headers()
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200 and 'application/pdf' in response.headers.get('content-type', ''):
                filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else "_" for c in title)[:100] + ".pdf"
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"✅ Downloaded: {title}")
                return True
                
        except Exception as e:
            logger.error(f"Error downloading {title}: {e}")
            
        return False
    
    def check_open_access(self, paper: Dict) -> Optional[str]:
        """Check if paper is available through open access sources"""
        title = paper.get("title", "")
        
        # Check arXiv
        if "arxiv" in paper.get("url", "").lower():
            return paper.get("pdf_url", paper.get("url", "").replace("abs", "pdf") + ".pdf")
        
        # Check DOI for open access indicators
        doi = paper.get("doi", "")
        if doi:
            # Try DOI.org resolver
            try:
                response = requests.head(f"https://doi.org/{doi}", timeout=10, allow_redirects=True)
                final_url = response.url
                
                # Check if redirected to open access source
                for open_source in OPEN_ACCESS_SOURCES:
                    if open_source in final_url:
                        return final_url
                        
            except Exception:
                pass
                
        return None
    
    def smart_download_with_selenium(self, paper: Dict) -> bool:
        """Enhanced Selenium-based download with better CAPTCHA handling"""
        if not self.driver:
            self.driver = self.initialize_driver()
            
        url = paper.get("url", "")
        title = paper.get("title", "")
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(2, 5))
            
            # Look for direct PDF links
            pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for link in pdf_links:
                pdf_url = link.get_attribute("href")
                if self.download_pdf_direct(pdf_url, title):
                    return True
            
            # Look for download buttons
            download_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Download')] | //a[contains(text(), 'Download')] | //a[contains(@class, 'download')]")
            
            for button in download_buttons:
                try:
                    button.click()
                    time.sleep(3)
                    # Handle any resulting downloads
                    break
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Selenium download error for {title}: {e}")
            
        return False
    
    def process_papers(self, papers: List[Dict]) -> int:
        """Process and download papers with multiple strategies"""
        downloaded = 0
        
        for paper in papers:
            if downloaded >= MAX_RESULTS:
                break
                
            title = paper.get("title", "Unknown")
            logger.info(f"Processing: {title}")
            
            # Strategy 1: Check for open access
            open_access_url = self.check_open_access(paper)
            if open_access_url:
                if self.download_pdf_direct(open_access_url, title):
                    downloaded += 1
                    continue
            
            # Strategy 2: Direct PDF download if URL points to PDF
            if paper.get("pdf_url"):
                if self.download_pdf_direct(paper["pdf_url"], title):
                    downloaded += 1
                    continue
            
            # Strategy 3: Smart Selenium approach
            if self.smart_download_with_selenium(paper):
                downloaded += 1
                continue
                
            logger.warning(f"Could not download: {title}")
            
        return downloaded
    
    def run(self):
        """Main execution method"""
        logger.info("Starting enhanced paper scraper...")
        
        all_papers = []
        
        # Scrape from IEEE
        ieee_papers = self.scrape_ieee_papers(SEARCH_PARAMS, MAX_RESULTS)
        all_papers.extend(ieee_papers)
        logger.info(f"Found {len(ieee_papers)} papers from IEEE")
        
        # Scrape from arXiv
        arxiv_papers = self.scrape_arxiv_papers(SEARCH_PARAMS["queryText"], MAX_RESULTS)
        all_papers.extend(arxiv_papers)
        logger.info(f"Found {len(arxiv_papers)} papers from arXiv")
        
        # Remove duplicates based on title similarity
        unique_papers = []
        seen_titles = set()
        for paper in all_papers:
            title_normalized = paper["title"].lower().strip()
            if title_normalized not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(title_normalized)
        
        logger.info(f"Total unique papers found: {len(unique_papers)}")
        
        # Process and download
        downloaded = self.process_papers(unique_papers)
        
        logger.info(f"Successfully downloaded {downloaded} papers")
        
        # Cleanup
        if self.driver:
            self.driver.quit()
            
        return downloaded

def main():
    scraper = EnhancedPaperScraper()
    try:
        downloaded = scraper.run()
        print(f"\n📦 Total papers downloaded: {downloaded}")
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    main()