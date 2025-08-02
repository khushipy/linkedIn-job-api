#!/usr/bin/env python3
"""
Enhanced LinkedIn Job Application Tool
- Applies to EasyApply jobs automatically
- Lists non-EasyApply jobs for manual application
- Uses resume parsing for job matching and suitability analysis
"""

import time
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import getpass
import pandas as pd

from resume_parser import ResumeParser, JobMatcher

class EnhancedLinkedInAutomation:
    def __init__(self, resume_path: str = None, min_match_score: float = 0.3):
        self.driver = None
        self.wait = None
        self.resume_path = resume_path
        self.min_match_score = min_match_score
        
        # Results storage
        self.easy_apply_jobs = []
        self.non_easy_apply_jobs = []
        self.applied_jobs = []
        self.failed_jobs = []
        self.suitable_jobs = []
        self.unsuitable_jobs = []
        
        # Resume analysis
        self.resume_data = None
        self.resume_parser = ResumeParser()
        self.job_matcher = JobMatcher()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('linkedin_enhanced.log'),
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

    def parse_resume(self):
        """Parse the provided resume file"""
        if not self.resume_path:
            self.logger.warning("No resume provided - job matching will be disabled")
            return
        
        try:
            self.resume_data = self.resume_parser.parse_resume(self.resume_path)
            self.logger.info(f"Resume parsed successfully. Found {len(self.resume_data['skills'])} skill categories")
            
            # Log resume summary
            skills_summary = []
            for category, skills in self.resume_data['skills'].items():
                if skills:
                    skills_summary.append(f"{category}: {', '.join(skills[:3])}{'...' if len(skills) > 3 else ''}")
            
            self.logger.info(f"Key skills: {'; '.join(skills_summary)}")
            self.logger.info(f"Experience level: {self.resume_data['experience_level']}")
            
        except Exception as e:
            self.logger.error(f"Failed to parse resume: {str(e)}")
            self.resume_data = None

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

    def search_jobs(self, keywords="", location=""):
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
            self.logger.info(f"Job search completed for: {keywords} in {location}")
            return True
            
        except Exception as e:
            self.logger.error(f"Job search failed: {str(e)}")
            return False

    def get_all_job_listings(self) -> List[Dict]:
        """Get all job listings (both EasyApply and non-EasyApply)"""
        try:
            # Scroll to load more jobs
            self.scroll_to_load_jobs()
            
            # Find all job cards
            job_cards = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'job-card-container')]"
            )
            
            all_jobs = []
            
            for i, card in enumerate(job_cards):
                try:
                    # Get job link
                    job_link_element = card.find_element(
                        By.XPATH, ".//a[contains(@class, 'job-card-list__title')]"
                    )
                    job_url = job_link_element.get_attribute('href')
                    job_title = job_link_element.text.strip()
                    
                    # Get company name
                    try:
                        company_element = card.find_element(
                            By.XPATH, ".//a[contains(@class, 'job-card-container__company-name')]"
                        )
                        company_name = company_element.text.strip()
                    except:
                        company_name = "Unknown Company"
                    
                    # Get location
                    try:
                        location_element = card.find_element(
                            By.XPATH, ".//li[contains(@class, 'job-card-container__metadata-item')]"
                        )
                        location = location_element.text.strip()
                    except:
                        location = "Unknown Location"
                    
                    # Check if EasyApply is available
                    has_easy_apply = False
                    try:
                        easy_apply_element = card.find_element(
                            By.XPATH, ".//span[contains(text(), 'Easy Apply')]"
                        )
                        has_easy_apply = True
                    except:
                        pass
                    
                    job_info = {
                        'title': job_title,
                        'company': company_name,
                        'location': location,
                        'url': job_url,
                        'has_easy_apply': has_easy_apply,
                        'description': '',  # Will be filled when visiting job page
                        'match_score': 0.0,
                        'is_suitable': False,
                        'match_explanation': ''
                    }
                    
                    all_jobs.append(job_info)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing job card {i}: {str(e)}")
                    continue
            
            self.logger.info(f"Found {len(all_jobs)} total job listings")
            return all_jobs
            
        except Exception as e:
            self.logger.error(f"Failed to get job listings: {str(e)}")
            return []

    def get_job_description(self, job_url: str) -> str:
        """Get job description from job page"""
        try:
            self.driver.get(job_url)
            time.sleep(2)
            
            # Try multiple selectors for job description
            description_selectors = [
                "//div[contains(@class, 'jobs-description-content__text')]",
                "//div[contains(@class, 'jobs-box__html-content')]",
                "//div[contains(@class, 'job-description')]"
            ]
            
            for selector in description_selectors:
                try:
                    description_element = self.driver.find_element(By.XPATH, selector)
                    return description_element.text
                except:
                    continue
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"Could not get job description for {job_url}: {str(e)}")
            return ""

    def analyze_and_categorize_jobs(self, jobs: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Analyze jobs and categorize into EasyApply and non-EasyApply"""
        easy_apply_jobs = []
        non_easy_apply_jobs = []
        
        for job in jobs:
            # Get job description for matching
            if self.resume_data:
                job['description'] = self.get_job_description(job['url'])
                
                # Analyze job suitability
                is_suitable, match_score, explanation = self.job_matcher.is_suitable_job(
                    self.resume_data, job['description'], job['title'], self.min_match_score
                )
                
                job['match_score'] = match_score
                job['is_suitable'] = is_suitable
                job['match_explanation'] = explanation
            
            # Categorize by EasyApply availability
            if job['has_easy_apply']:
                easy_apply_jobs.append(job)
            else:
                non_easy_apply_jobs.append(job)
        
        # Sort by match score if resume analysis is available
        if self.resume_data:
            easy_apply_jobs = sorted(easy_apply_jobs, key=lambda x: x['match_score'], reverse=True)
            non_easy_apply_jobs = sorted(non_easy_apply_jobs, key=lambda x: x['match_score'], reverse=True)
        
        self.logger.info(f"Categorized jobs: {len(easy_apply_jobs)} EasyApply, {len(non_easy_apply_jobs)} non-EasyApply")
        
        return easy_apply_jobs, non_easy_apply_jobs

    def apply_to_easy_apply_jobs(self, easy_apply_jobs: List[Dict], max_applications: int = 50):
        """Apply to suitable EasyApply jobs"""
        applications_sent = 0
        
        for job in easy_apply_jobs:
            if applications_sent >= max_applications:
                break
            
            # Skip if resume analysis shows job is not suitable
            if self.resume_data and not job['is_suitable']:
                self.unsuitable_jobs.append(job)
                self.logger.info(f"Skipping unsuitable job: {job['title']} at {job['company']} (Score: {job['match_score']:.2f})")
                continue
            
            # Apply to the job
            if self.apply_to_job(job):
                applications_sent += 1
                self.suitable_jobs.append(job)
            
            # Add delay between applications
            time.sleep(3)
        
        self.logger.info(f"Applied to {applications_sent} jobs automatically")

    def apply_to_job(self, job: Dict) -> bool:
        """Apply to a specific job using EasyApply"""
        try:
            self.driver.get(job['url'])
            time.sleep(3)
            
            # Look for EasyApply button
            easy_apply_button = None
            try:
                easy_apply_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]")
                ))
            except:
                try:
                    easy_apply_button = self.driver.find_element(
                        By.XPATH, "//button[contains(text(), 'Easy Apply')]"
                    )
                except:
                    self.logger.warning(f"No EasyApply button found for job: {job['title']}")
                    return False
            
            if easy_apply_button:
                easy_apply_button.click()
                time.sleep(2)
                
                # Handle the application process
                if self.handle_application_process():
                    self.applied_jobs.append(job)
                    self.logger.info(f"Successfully applied to: {job['title']} at {job['company']}")
                    return True
                else:
                    self.failed_jobs.append(job)
                    return False
            
        except Exception as e:
            self.logger.error(f"Failed to apply to job {job['title']}: {str(e)}")
            self.failed_jobs.append(job)
            return False

    def handle_application_process(self) -> bool:
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

    def scroll_to_load_jobs(self):
        """Scroll down to load more job listings"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def generate_comprehensive_report(self):
        """Generate comprehensive report with all job categories"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create comprehensive report
        report = {
            'timestamp': timestamp,
            'resume_analysis': {
                'resume_provided': self.resume_data is not None,
                'skills_found': self.resume_data['skills'] if self.resume_data else {},
                'experience_level': self.resume_data['experience_level'] if self.resume_data else 'unknown',
                'years_experience': self.resume_data['years_experience'] if self.resume_data else 0
            },
            'job_statistics': {
                'total_jobs_found': len(self.easy_apply_jobs) + len(self.non_easy_apply_jobs),
                'easy_apply_jobs': len(self.easy_apply_jobs),
                'non_easy_apply_jobs': len(self.non_easy_apply_jobs),
                'applications_sent': len(self.applied_jobs),
                'applications_failed': len(self.failed_jobs),
                'suitable_jobs': len(self.suitable_jobs),
                'unsuitable_jobs': len(self.unsuitable_jobs)
            },
            'applied_jobs': self.applied_jobs,
            'failed_jobs': self.failed_jobs,
            'non_easy_apply_jobs': self.non_easy_apply_jobs,
            'unsuitable_jobs': self.unsuitable_jobs
        }
        
        # Save main report
        report_filename = f'linkedin_comprehensive_report_{timestamp}.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create CSV for non-EasyApply jobs (for manual application)
        if self.non_easy_apply_jobs:
            df_non_easy = pd.DataFrame(self.non_easy_apply_jobs)
            csv_filename = f'non_easy_apply_jobs_{timestamp}.csv'
            df_non_easy.to_csv(csv_filename, index=False)
            self.logger.info(f"Non-EasyApply jobs saved to: {csv_filename}")
        
        # Print summary
        self.print_summary_report(report)
        
        return report_filename

    def print_summary_report(self, report):
        """Print a formatted summary report"""
        print("\n" + "="*60)
        print("ENHANCED LINKEDIN JOB AUTOMATION REPORT")
        print("="*60)
        
        stats = report['job_statistics']
        resume_info = report['resume_analysis']
        
        print(f"📊 JOB STATISTICS:")
        print(f"   Total Jobs Found: {stats['total_jobs_found']}")
        print(f"   EasyApply Jobs: {stats['easy_apply_jobs']}")
        print(f"   Non-EasyApply Jobs: {stats['non_easy_apply_jobs']}")
        print(f"   Applications Sent: {stats['applications_sent']}")
        print(f"   Applications Failed: {stats['applications_failed']}")
        
        if resume_info['resume_provided']:
            print(f"\n🎯 RESUME MATCHING:")
            print(f"   Suitable Jobs: {stats['suitable_jobs']}")
            print(f"   Unsuitable Jobs: {stats['unsuitable_jobs']}")
            print(f"   Experience Level: {resume_info['experience_level']}")
            print(f"   Years Experience: {resume_info['years_experience']}")
        
        if stats['non_easy_apply_jobs'] > 0:
            print(f"\n📋 MANUAL APPLICATION REQUIRED:")
            print(f"   {stats['non_easy_apply_jobs']} jobs require manual application")
            print(f"   Check 'non_easy_apply_jobs_*.csv' for the complete list")
        
        success_rate = (stats['applications_sent'] / (stats['applications_sent'] + stats['applications_failed']) * 100) if (stats['applications_sent'] + stats['applications_failed']) > 0 else 0
        print(f"\n✅ SUCCESS RATE: {success_rate:.1f}%")
        print("="*60)

    def run_enhanced_automation(self, email, password, keywords="", location="", max_applications=50):
        """Main method to run the enhanced automation process"""
        try:
            # Parse resume if provided
            if self.resume_path:
                self.parse_resume()
            
            # Setup driver and login
            self.setup_driver()
            
            if not self.login_to_linkedin(email, password):
                self.logger.error("Failed to login. Exiting...")
                return
            
            # Search for jobs
            if not self.search_jobs(keywords, location):
                self.logger.error("Failed to search jobs. Exiting...")
                return
            
            # Get all job listings
            all_jobs = self.get_all_job_listings()
            
            if not all_jobs:
                self.logger.warning("No job listings found")
                return
            
            # Analyze and categorize jobs
            easy_apply_jobs, non_easy_apply_jobs = self.analyze_and_categorize_jobs(all_jobs)
            
            self.easy_apply_jobs = easy_apply_jobs
            self.non_easy_apply_jobs = non_easy_apply_jobs
            
            # Apply to suitable EasyApply jobs
            if easy_apply_jobs:
                self.logger.info(f"Starting automatic applications to {len(easy_apply_jobs)} EasyApply jobs...")
                self.apply_to_easy_apply_jobs(easy_apply_jobs, max_applications)
            
            # Generate comprehensive report
            report_file = self.generate_comprehensive_report()
            self.logger.info(f"Comprehensive report saved to: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Enhanced automation failed: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

def main():
    """Main function to run the enhanced LinkedIn automation"""
    print("Enhanced LinkedIn Job Automation Tool")
    print("="*50)
    
    # Get user credentials
    email = input("Enter your LinkedIn email: ")
    password = getpass.getpass("Enter your LinkedIn password: ")
    
    # Get search criteria
    keywords = input("Enter job keywords (optional): ")
    location = input("Enter location (optional): ")
    
    # Get resume path
    resume_path = input("Enter path to your resume file (optional, for job matching): ").strip()
    if resume_path and not os.path.exists(resume_path):
        print(f"Warning: Resume file not found at {resume_path}")
        resume_path = None
    
    # Get matching threshold
    if resume_path:
        try:
            min_score = float(input("Enter minimum job match score (0.0-1.0, default 0.3): ") or "0.3")
            min_score = max(0.0, min(1.0, min_score))
        except ValueError:
            min_score = 0.3
    else:
        min_score = 0.3
    
    try:
        max_apps = int(input("Maximum applications to send (default 50): ") or "50")
    except ValueError:
        max_apps = 50
    
    # Create and run enhanced automation
    automation = EnhancedLinkedInAutomation(resume_path, min_score)
    automation.run_enhanced_automation(email, password, keywords, location, max_apps)

if __name__ == "__main__":
    main()
