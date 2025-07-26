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
    "queryText": "brain tumor segmentation",
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

# Setup logging with UTF-8 encoding to handle emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set console encoding for Windows
import sys
if sys.platform.startswith('win'):
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class EnhancedPaperScraper:
    def __init__(self, institutional_access=False, proxy_url=None, include_conferences=True, include_journals=True):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.driver = None
        self.institutional_access = institutional_access
        self.proxy_url = proxy_url
        self.has_ieee_access = False
        self.include_conferences = include_conferences
        self.include_journals = include_journals
        
    def check_institutional_access(self) -> bool:
        """Check if we have institutional access to IEEE Xplore"""
        try:
            if not self.driver:
                self.driver = self.initialize_driver()
            
            # Navigate to IEEE Xplore
            self.driver.get("https://ieeexplore.ieee.org/")
            time.sleep(3)
            
            # Look for institutional access indicators
            page_source = self.driver.page_source.lower()
            
            # Check for common institutional access indicators
            institutional_indicators = [
                "institutional access",
                "university access", 
                "library access",
                "campus access",
                "authenticated",
                "institutional login",
                "shibboleth",
                "openathens"
            ]
            
            for indicator in institutional_indicators:
                if indicator in page_source:
                    logger.info("✅ Institutional access detected!")
                    self.has_ieee_access = True
                    return True
            
            # Try to access a sample paper to test download capabilities
            test_url = "https://ieeexplore.ieee.org/document/8578166"  # Random IEEE paper
            self.driver.get(test_url)
            time.sleep(3)
            
            # Look for PDF download button
            pdf_buttons = self.driver.find_elements(By.XPATH, 
                "//a[contains(@class, 'pdf')] | //button[contains(text(), 'PDF')] | //a[contains(text(), 'Download PDF')]")
            
            if pdf_buttons:
                # Check if button is clickable (not grayed out)
                for button in pdf_buttons:
                    if button.is_enabled() and button.is_displayed():
                        logger.info("✅ IEEE PDF download access confirmed!")
                        self.has_ieee_access = True
                        return True
                        
        except Exception as e:
            logger.error(f"Error checking institutional access: {e}")
            
        logger.info("No institutional IEEE access detected")
        return False
    
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
    
    def setup_institutional_proxy(self):
        """Setup proxy if institutional access requires it"""
        if self.proxy_url:
            proxies = {
                'http': self.proxy_url,
                'https': self.proxy_url
            }
            self.session.proxies.update(proxies)
    
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
        
        # Set download directory
        prefs = {
            "download.default_directory": DOWNLOAD_FOLDER,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
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
                        "publication": record.get("publicationTitle", ""),
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
                        "publication": "arXiv preprint",
                        "source": "arXiv",
                        "pdf_url": entry.find("id").text.replace("abs", "pdf") + ".pdf"
                    }
                    papers.append(paper)
                    
        except Exception as e:
            logger.error(f"Error scraping arXiv papers: {e}")
            
        return papers
    
    def filter_paper_types(self, papers: List[Dict]) -> List[Dict]:
        """Filter papers based on conference/journal preferences"""
        if self.include_conferences and self.include_journals:
            return papers
        
        filtered_papers = []
        for paper in papers:
            paper_type = self.classify_paper_type(paper)
            
            if paper_type == "conference" and self.include_conferences:
                filtered_papers.append(paper)
            elif paper_type == "journal" and self.include_journals:
                filtered_papers.append(paper)
            elif paper_type == "unknown":
                # Include unknown types to be safe
                filtered_papers.append(paper)
                
        return filtered_papers
    
    def classify_paper_type(self, paper: Dict) -> str:
        """Classify paper as conference or journal based on publication info"""
        title = paper.get("title", "").lower()
        url = paper.get("url", "").lower()
        
        # Conference indicators
        conference_keywords = [
            "conference", "proceedings", "workshop", "symposium", 
            "congress", "summit", "meeting", "colloquium", "forum",
            "icml", "nips", "iclr", "cvpr", "iccv", "eccv", "aaai",
            "sigkdd", "sigir", "chi", "cscw", "uist", "acl", "emnlp",
            "interspeech", "icassp", "infocom", "mobicom", "sensys"
        ]
        
        # Journal indicators  
        journal_keywords = [
            "journal", "transactions", "letters", "review", "magazine",
            "ieee trans", "acm trans", "nature", "science", "cell",
            "pnas", "jmlr", "tpami", "tnnls", "tac", "ton", "tkde"
        ]
        
        # Check publication venue or title
        publication_venue = paper.get("publication", "").lower()
        combined_text = f"{title} {publication_venue} {url}"
        
        # Count matches
        conference_matches = sum(1 for keyword in conference_keywords if keyword in combined_text)
        journal_matches = sum(1 for keyword in journal_keywords if keyword in combined_text)
        
        if conference_matches > journal_matches:
            return "conference"
        elif journal_matches > conference_matches:
            return "journal"
        else:
            return "unknown"
    
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
    
    def download_ieee_paper_institutional(self, paper: Dict) -> bool:
        """Download paper directly from IEEE using institutional access"""
        if not self.has_ieee_access:
            return False
            
        try:
            if not self.driver:
                self.driver = self.initialize_driver()
                
            url = paper.get("url", "")
            title = paper.get("title", "")
            
            logger.info(f"Attempting institutional download: {title}")
            
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            # Look for various PDF download elements
            pdf_selectors = [
                "//a[contains(@class, 'pdf')]",
                "//button[contains(text(), 'PDF')]",
                "//a[contains(text(), 'Download PDF')]",
                "//button[contains(@class, 'pdf')]",
                "//a[@title='Download PDF']",
                "//span[text()='PDF']/parent::*",
                "//i[contains(@class, 'pdf')]/parent::*",
                ".pdf-btn, .download-pdf, .btn-pdf"
            ]
            
            for selector in pdf_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Try clicking the download button
                            self.driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)
                            
                            # Check if download started or new tab opened
                            if len(self.driver.window_handles) > 1:
                                # Switch to new tab with PDF
                                self.driver.switch_to.window(self.driver.window_handles[-1])
                                current_url = self.driver.current_url
                                
                                if current_url.endswith('.pdf') or 'pdf' in current_url:
                                    # Direct PDF URL found
                                    if self.download_pdf_direct(current_url, title):
                                        self.driver.close()
                                        self.driver.switch_to.window(self.driver.window_handles[0])
                                        return True
                                
                                self.driver.close()
                                self.driver.switch_to.window(self.driver.window_handles[0])
                            
                            break
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Alternative: Look for direct PDF links in page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find iframe or embed with PDF
            for tag in ['iframe', 'embed', 'object']:
                elements = soup.find_all(tag)
                for elem in elements:
                    src = elem.get('src') or elem.get('data')
                    if src and 'pdf' in src.lower():
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://ieeexplore.ieee.org' + src
                            
                        if self.download_pdf_direct(src, title):
                            return True
                            
        except Exception as e:
            logger.error(f"Error in institutional download for {title}: {e}")
            
        return False
    
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
        """Process and download papers with institutional access priority"""
        downloaded = 0
        
        # Separate IEEE papers from others if we have institutional access
        ieee_papers = [p for p in papers if p.get("source") == "IEEE"]
        other_papers = [p for p in papers if p.get("source") != "IEEE"]
        
        # Prioritize based on access
        if self.has_ieee_access:
            # IEEE first, then others
            prioritized_papers = ieee_papers + other_papers
            logger.info(f"Using institutional access - prioritizing {len(ieee_papers)} IEEE papers")
        else:
            # Open access first, then IEEE
            prioritized_papers = other_papers + ieee_papers
            logger.info(f"No institutional access - prioritizing {len(other_papers)} open access papers")
        
        for paper in prioritized_papers:
            if downloaded >= MAX_RESULTS:
                break
                
            title = paper.get("title", "Unknown")
            source = paper.get("source", "Unknown")
            logger.info(f"Processing [{source}]: {title[:60]}...")
            
            success = False
            
            # Strategy 1: Institutional access for IEEE papers
            if self.has_ieee_access and paper.get("source") == "IEEE":
                success = self.download_ieee_paper_institutional(paper)
                if success:
                    downloaded += 1
                    continue
            
            # Strategy 2: Direct open access
            if paper.get("source") == "arXiv" and paper.get("pdf_url"):
                success = self.download_pdf_direct(paper["pdf_url"], title)
                if success:
                    downloaded += 1
                    continue
            
            # Strategy 3: Check for other open access sources
            open_access_url = self.check_open_access(paper)
            if open_access_url:
                success = self.download_pdf_direct(open_access_url, title)
                if success:
                    downloaded += 1
                    continue
            
            # Strategy 4: General selenium approach
            success = self.smart_download_with_selenium(paper)
            if success:
                downloaded += 1
                continue
                
            logger.warning(f"Could not download: {title[:60]}...")
            
        return downloaded
    
    def run(self):
        """Main execution method with institutional access detection"""
        logger.info("Starting enhanced paper scraper...")
        
        # Setup proxy if provided
        if self.proxy_url:
            self.setup_institutional_proxy()
        
        # Check for institutional access first
        if self.institutional_access or self.check_institutional_access():
            logger.info("Institutional access mode enabled")
        else:
            logger.info("Open access mode - will prioritize free sources")
        
        all_papers = []
        
        # Scrape from IEEE (prioritized if institutional access)
        ieee_papers = self.scrape_ieee_papers(SEARCH_PARAMS, MAX_RESULTS * 2)  # Get more if we have access
        all_papers.extend(ieee_papers)
        logger.info(f"Found {len(ieee_papers)} papers from IEEE")
        
        # Scrape from arXiv
        arxiv_papers = self.scrape_arxiv_papers(SEARCH_PARAMS["queryText"], MAX_RESULTS)
        all_papers.extend(arxiv_papers)
        logger.info(f"Found {len(arxiv_papers)} papers from arXiv")
        
        # Filter by paper type (conference/journal)
        if not (self.include_conferences and self.include_journals):
            before_filter = len(all_papers)
            all_papers = self.filter_paper_types(all_papers)
            filter_type = []
            if self.include_conferences: filter_type.append("conferences")
            if self.include_journals: filter_type.append("journals")
            logger.info(f"Filtered to {len(all_papers)} papers (showing only {' and '.join(filter_type)}) from {before_filter} total")
        
        # Remove duplicates based on title similarity
        unique_papers = []
        seen_titles = set()
        for paper in all_papers:
            title_normalized = paper["title"].lower().strip()
            if title_normalized not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(title_normalized)
        
        logger.info(f"Total unique papers found: {len(unique_papers)}")
        
        # Process and download with priority logic
        downloaded = self.process_papers(unique_papers)
        
        logger.info(f"Successfully downloaded {downloaded} papers")
        
        # Cleanup
        if self.driver:
            self.driver.quit()
            
        return downloaded

def main():
    """Main function with institutional access and paper type options"""
    print("Academic Paper Scraper")
    print("=" * 50)
    
    # Check if user has institutional access
    has_institutional = input("Do you have institutional access to IEEE Xplore? (y/n): ").lower().startswith('y')
    proxy_url = None
    
    if has_institutional:
        print("\nInstitutional Access Options:")
        print("1. Direct access (on campus network)")
        print("2. VPN/Proxy access")
        choice = input("Choose option (1 or 2): ").strip()
        
        if choice == "2":
            proxy_url = input("Enter proxy URL (e.g., http://proxy.university.edu:8080): ").strip()
    
    # Paper type preferences
    print("\nPaper Type Preferences:")
    print("1. Both conference and journal papers")
    print("2. Conference papers only (ICML, NIPS, CVPR, etc.)")
    print("3. Journal papers only (IEEE Trans, Nature, etc.)")
    
    paper_choice = input("Choose paper types (1, 2, or 3): ").strip()
    
    include_conferences = paper_choice in ["1", "2"]
    include_journals = paper_choice in ["1", "3"]
    
    scraper = EnhancedPaperScraper(
        institutional_access=has_institutional,
        proxy_url=proxy_url if proxy_url else None,
        include_conferences=include_conferences,
        include_journals=include_journals
    )
    
    try:
        downloaded = scraper.run()
        print(f"\nTotal papers downloaded: {downloaded}")
        print(f"Files saved to: {DOWNLOAD_FOLDER}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logger.error(f"Main execution error: {e}")
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    main()