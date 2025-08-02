#!/usr/bin/env python3
"""
LinkedIn EasyApply Automation Tool
Automatically applies to jobs using LinkedIn's EasyApply feature
"""

import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import getpass

class LinkedInEasyApply:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.applied_jobs = []
        self.failed_jobs = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('linkedin_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        self.logger.info("Chrome WebDriver initialized successfully")

    def login_to_linkedin(self, email, password):
        """Login to LinkedIn with provided credentials"""
        try:
            self.logger.info("Navigating to LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.send_keys(email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            self.wait.until(EC.url_contains("linkedin.com/feed"))
            self.logger.info("Successfully logged into LinkedIn")
            return True
            
        except TimeoutException:
            self.logger.error("Login failed - timeout or incorrect credentials")
            return False
        except Exception as e:
            self.logger.error(f"Login failed with error: {str(e)}")
            return False

    def search_jobs(self, keywords="", location="", job_type=""):
        """Search for jobs with specified criteria"""
        try:
            # Navigate to jobs page
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Enter search keywords
            if keywords:
                keyword_field = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[contains(@placeholder, 'Search jobs')]")
                ))
                keyword_field.clear()
                keyword_field.send_keys(keywords)
            
            # Enter location
            if location:
                location_field = self.driver.find_element(
                    By.XPATH, "//input[contains(@placeholder, 'City, state, or zip code')]"
                )
                location_field.clear()
                location_field.send_keys(location)
            
            # Click search button
            search_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'jobs-search-box__submit-button')]")
            search_button.click()
            
            time.sleep(3)
            
            # Filter for EasyApply jobs only
            try:
                easy_apply_filter = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Easy Apply')]")
                ))
                easy_apply_filter.click()
                time.sleep(2)
                self.logger.info("Applied EasyApply filter")
            except:
                self.logger.warning("Could not find EasyApply filter")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Job search failed: {str(e)}")
            return False

    def get_job_listings(self):
        """Get all job listings from the current search results"""
        try:
            # Scroll to load more jobs
            self.scroll_to_load_jobs()
            
            # Find all job cards
            job_cards = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'job-card-container')]//a[contains(@class, 'job-card-list__title')]"
            )
            
            job_links = []
            for card in job_cards:
                try:
                    job_link = card.get_attribute('href')
                    if job_link:
                        job_links.append(job_link)
                except:
                    continue
            
            self.logger.info(f"Found {len(job_links)} job listings")
            return job_links
            
        except Exception as e:
            self.logger.error(f"Failed to get job listings: {str(e)}")
            return []

    def scroll_to_load_jobs(self):
        """Scroll down to load more job listings"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def apply_to_job(self, job_url):
        """Apply to a specific job using EasyApply"""
        try:
            self.driver.get(job_url)
            time.sleep(3)
            
            # Look for EasyApply button
            easy_apply_button = None
            try:
                easy_apply_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]")
                ))
            except:
                # Alternative selector
                try:
                    easy_apply_button = self.driver.find_element(
                        By.XPATH, "//button[contains(text(), 'Easy Apply')]"
                    )
                except:
                    self.logger.warning(f"No EasyApply button found for job: {job_url}")
                    return False
            
            if easy_apply_button:
                easy_apply_button.click()
                time.sleep(2)
                
                # Handle the application process
                if self.handle_application_process():
                    job_title = self.get_job_title()
                    self.applied_jobs.append({
                        'url': job_url,
                        'title': job_title,
                        'status': 'Applied'
                    })
                    self.logger.info(f"Successfully applied to: {job_title}")
                    return True
                else:
                    self.failed_jobs.append({
                        'url': job_url,
                        'title': self.get_job_title(),
                        'status': 'Failed'
                    })
                    return False
            
        except Exception as e:
            self.logger.error(f"Failed to apply to job {job_url}: {str(e)}")
            self.failed_jobs.append({
                'url': job_url,
                'title': 'Unknown',
                'status': f'Error: {str(e)}'
            })
            return False

    def handle_application_process(self):
        """Handle the EasyApply application process"""
        try:
            max_attempts = 5
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    # Look for Submit button
                    submit_button = self.driver.find_element(
                        By.XPATH, "//button[contains(@aria-label, 'Submit application')]"
                    )
                    if submit_button.is_enabled():
                        submit_button.click()
                        time.sleep(2)
                        
                        # Check if application was submitted
                        try:
                            success_message = self.driver.find_element(
                                By.XPATH, "//h3[contains(text(), 'Application submitted')]"
                            )
                            return True
                        except:
                            pass
                    
                    # Look for Next button
                    next_button = self.driver.find_element(
                        By.XPATH, "//button[contains(@aria-label, 'Continue to next step')]"
                    )
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(2)
                        attempt += 1
                        continue
                    
                    # Look for Review button
                    review_button = self.driver.find_element(
                        By.XPATH, "//button[contains(@aria-label, 'Review your application')]"
                    )
                    if review_button.is_enabled():
                        review_button.click()
                        time.sleep(2)
                        attempt += 1
                        continue
                        
                except NoSuchElementException:
                    # If we can't find any buttons, the application might be complete
                    try:
                        success_message = self.driver.find_element(
                            By.XPATH, "//h3[contains(text(), 'Application submitted')]"
                        )
                        return True
                    except:
                        break
                
                attempt += 1
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in application process: {str(e)}")
            return False

    def get_job_title(self):
        """Get the job title from the current job page"""
        try:
            title_element = self.driver.find_element(
                By.XPATH, "//h1[contains(@class, 'job-title')]"
            )
            return title_element.text
        except:
            return "Unknown Job Title"

    def run_automation(self, email, password, keywords="", location="", max_applications=50):
        """Main method to run the entire automation process"""
        try:
            self.setup_driver()
            
            # Login to LinkedIn
            if not self.login_to_linkedin(email, password):
                self.logger.error("Failed to login. Exiting...")
                return
            
            # Search for jobs
            if not self.search_jobs(keywords, location):
                self.logger.error("Failed to search jobs. Exiting...")
                return
            
            # Get job listings
            job_links = self.get_job_listings()
            
            if not job_links:
                self.logger.warning("No job listings found")
                return
            
            # Apply to jobs
            applications_sent = 0
            for job_url in job_links[:max_applications]:
                if self.apply_to_job(job_url):
                    applications_sent += 1
                
                # Add delay between applications
                time.sleep(3)
                
                self.logger.info(f"Progress: {applications_sent}/{min(len(job_links), max_applications)} applications sent")
            
            # Generate report
            self.generate_report()
            
        except Exception as e:
            self.logger.error(f"Automation failed: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

    def generate_report(self):
        """Generate a report of the automation results"""
        report = {
            'total_applied': len(self.applied_jobs),
            'total_failed': len(self.failed_jobs),
            'applied_jobs': self.applied_jobs,
            'failed_jobs': self.failed_jobs
        }
        
        # Save to JSON file
        with open('application_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("LINKEDIN EASYAPPLY AUTOMATION REPORT")
        print("="*50)
        print(f"Total Applications Sent: {report['total_applied']}")
        print(f"Total Failed Applications: {report['total_failed']}")
        print(f"Success Rate: {(report['total_applied']/(report['total_applied']+report['total_failed'])*100):.1f}%" if (report['total_applied']+report['total_failed']) > 0 else "0%")
        print("\nDetailed report saved to 'application_report.json'")
        print("="*50)

def main():
    """Main function to run the LinkedIn EasyApply automation"""
    print("LinkedIn EasyApply Automation Tool")
    print("="*40)
    
    # Get user credentials
    email = input("Enter your LinkedIn email: ")
    password = getpass.getpass("Enter your LinkedIn password: ")
    
    # Get search criteria
    keywords = input("Enter job keywords (optional): ")
    location = input("Enter location (optional): ")
    
    try:
        max_apps = int(input("Maximum applications to send (default 50): ") or "50")
    except ValueError:
        max_apps = 50
    
    # Create and run automation
    automation = LinkedInEasyApply()
    automation.run_automation(email, password, keywords, location, max_apps)

if __name__ == "__main__":
    main()
