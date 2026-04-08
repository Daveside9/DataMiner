import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from datetime import datetime

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url, selectors=None, use_selenium=False):
        """
        Scrape data from a URL using either requests+BeautifulSoup or Selenium
        
        Args:
            url (str): The URL to scrape
            selectors (dict): CSS selectors for specific data points
            use_selenium (bool): Whether to use Selenium for dynamic content
        
        Returns:
            dict: Scraped data with timestamp
        """
        try:
            if use_selenium:
                return self._scrape_with_selenium(url, selectors)
            else:
                return self._scrape_with_requests(url, selectors)
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _scrape_with_requests(self, url, selectors):
        """Scrape using requests and BeautifulSoup"""
        response = self.session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "method": "requests",
            "data": {}
        }
        
        if selectors:
            # Extract specific data using provided selectors
            for key, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        data["data"][key] = elements[0].get_text(strip=True)
                    else:
                        data["data"][key] = [elem.get_text(strip=True) for elem in elements]
                else:
                    data["data"][key] = None
        else:
            # Extract common data points automatically
            data["data"] = self._extract_common_data(soup)
        
        return data
    
    def _scrape_with_selenium(self, url, selectors):
        """Scrape using Selenium for dynamic content"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        try:
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            data = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "method": "selenium",
                "data": {}
            }
            
            if selectors:
                # Extract specific data using provided selectors
                for key, selector_value in selectors.items():
                    try:
                        # Handle multiple selectors separated by commas
                        if ',' in selector_value:
                            selectors_list = [s.strip() for s in selector_value.split(',')]
                        else:
                            selectors_list = [selector_value.strip()]
                        
                        found_elements = []
                        for selector in selectors_list:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                if elements:
                                    found_elements.extend([elem.text.strip() for elem in elements if elem.text.strip()])
                                    break  # Use first working selector
                            except:
                                continue
                        
                        if found_elements:
                            # Remove duplicates while preserving order
                            unique_elements = []
                            seen = set()
                            for elem in found_elements:
                                if elem not in seen and len(elem) > 1:  # Filter out single characters
                                    unique_elements.append(elem)
                                    seen.add(elem)
                            
                            data["data"][key] = unique_elements[:50]  # Limit to 50 items
                        else:
                            data["data"][key] = []
                            
                    except Exception as e:
                        data["data"][key] = []
                        print(f"Error extracting {key}: {str(e)}")
            else:
                # Extract common data points automatically
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                data["data"] = self._extract_common_data(soup)
            
            return data
        
        finally:
            driver.quit()
    
    def _extract_common_data(self, soup):
        """Extract common data points from a webpage"""
        common_data = {}
        
        # Page title
        title = soup.find('title')
        common_data['title'] = title.get_text(strip=True) if title else None
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        common_data['description'] = meta_desc.get('content') if meta_desc else None
        
        # All headings
        headings = []
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings.extend([h.get_text(strip=True) for h in h_tags])
        common_data['headings'] = headings
        
        # All links
        links = soup.find_all('a', href=True)
        common_data['links'] = [{'text': link.get_text(strip=True), 'href': link['href']} for link in links[:10]]  # Limit to first 10
        
        # All paragraphs (first 5)
        paragraphs = soup.find_all('p')
        common_data['paragraphs'] = [p.get_text(strip=True) for p in paragraphs[:5]]
        
        return common_data
    
    def test_selectors(self, url, selectors):
        """Test CSS selectors on a webpage"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = {}
            for key, selector in selectors.items():
                elements = soup.select(selector)
                results[key] = {
                    'found': len(elements),
                    'sample_text': elements[0].get_text(strip=True) if elements else None
                }
            
            return results
        except Exception as e:
            return {"error": str(e)}