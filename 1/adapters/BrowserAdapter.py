"""
BrowserAdapter.py
"""
import time
from .ChainableAdapter import ChainableAdapter

class BrowserAdapter(ChainableAdapter):
    def __init__(self, params=None):
        super().__init__(params)
        self._driver = None
        self._url = None
        self._actions = []

    def open(self, url=None):
        """Open the specified URL"""
        self._url = url
        return self

    def wait(self, seconds=2):
        """Wait for a specified number of seconds"""
        self._actions.append(('wait', seconds))
        return self

    def click(self, selector):
        """Click on an element with the specified selector"""
        self._actions.append(('click', selector))
        return self

    def scroll(self, amount=500):
        """Scroll the page by specified amount"""
        self._actions.append(('scroll', amount))
        return self

    def extract(self, config):
        """Extract data from the page based on config"""
        self._actions.append(('extract', config))
        return self

    def _execute_self(self, input_data=None):
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # Set up headless Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Try different initialization methods
            try:
                # Try using WebDriver Manager if available
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    self._driver = webdriver.Chrome(service=service, options=chrome_options)
                except ImportError:
                    print("webdriver-manager not found, trying direct Chrome initialization")
                    self._driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                # Try Firefox as fallback
                try:
                    print("Chrome initialization failed, trying Firefox")
                    from selenium.webdriver.firefox.options import Options as FirefoxOptions
                    firefox_options = FirefoxOptions()
                    firefox_options.add_argument("--headless")
                    self._driver = webdriver.Firefox(options=firefox_options)
                except Exception as ff_error:
                    raise RuntimeError(
                        f"Browser initialization failed. Please run: pip install webdriver-manager\nOriginal error: {str(e)}")


            # Use provided URL or use input_data if it's a string
            url = self._url
            if url is None and isinstance(input_data, str) and input_data.startswith('http'):
                url = input_data

            if url:
                self._driver.get(url)

                # Execute all actions in sequence
                results = {}
                for action_type, action_param in self._actions:
                    if action_type == 'wait':
                        time.sleep(action_param)

                    elif action_type == 'click':
                        element = WebDriverWait(self._driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, action_param))
                        )
                        element.click()

                    elif action_type == 'scroll':
                        self._driver.execute_script(f"window.scrollBy(0, {action_param})")

                    elif action_type == 'extract':
                        extracted_data = {}
                        for key, selector in action_param.items():
                            if isinstance(selector, dict) and 'selector' in selector:
                                css_selector = selector['selector']
                                attribute = selector.get('attribute', 'innerText')
                                multiple = selector.get('multiple', False)

                                if multiple:
                                    elements = self._driver.find_elements(By.CSS_SELECTOR, css_selector)
                                    extracted_data[key] = [
                                        elem.get_attribute(attribute) if attribute != 'innerText'
                                        else elem.text for elem in elements
                                    ]
                                else:
                                    element = self._driver.find_element(By.CSS_SELECTOR, css_selector)
                                    extracted_data[key] = (element.get_attribute(attribute)
                                                        if attribute != 'innerText' else element.text)
                            else:
                                # Simple case: selector is just a string (CSS selector)
                                element = self._driver.find_element(By.CSS_SELECTOR, selector)
                                extracted_data[key] = element.text

                        results = extracted_data

                # Get page source if no explicit extract was performed
                if not results and not any(a[0] == 'extract' for a in self._actions):
                    results = self._driver.page_source

            self._driver.quit()
            return results

        except Exception as e:
            if self._driver:
                self._driver.quit()
            raise RuntimeError(f"Browser operation failed: {str(e)}")