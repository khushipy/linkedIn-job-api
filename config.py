#!/usr/bin/env python3
"""
Configuration file for LinkedIn EasyApply Automation Tool
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the LinkedIn automation tool"""
    
    # LinkedIn URLs
    LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
    LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/"
    
    # Selenium settings
    WEBDRIVER_TIMEOUT = 10
    PAGE_LOAD_TIMEOUT = 30
    IMPLICIT_WAIT = 5
    
    # Application settings
    DEFAULT_MAX_APPLICATIONS = 50
    APPLICATION_DELAY = 3  # seconds between applications
    SCROLL_DELAY = 2  # seconds between scrolls
    
    # Retry settings
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 5  # seconds
    
    # File paths
    LOG_FILE = "linkedin_automation.log"
    REPORT_FILE = "application_report.json"
    
    # Chrome options
    CHROME_OPTIONS = [
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080"
    ]
    
    # User agent
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # XPath selectors (can be updated if LinkedIn changes their UI)
    SELECTORS = {
        'login_email': "//input[@id='username']",
        'login_password': "//input[@id='password']",
        'login_button': "//button[@type='submit']",
        'job_search_keywords': "//input[contains(@placeholder, 'Search jobs')]",
        'job_search_location': "//input[contains(@placeholder, 'City, state, or zip code')]",
        'search_button': "//button[contains(@class, 'jobs-search-box__submit-button')]",
        'easy_apply_filter': "//button[contains(text(), 'Easy Apply')]",
        'job_cards': "//div[contains(@class, 'job-card-container')]//a[contains(@class, 'job-card-list__title')]",
        'easy_apply_button': "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]",
        'submit_button': "//button[contains(@aria-label, 'Submit application')]",
        'next_button': "//button[contains(@aria-label, 'Continue to next step')]",
        'review_button': "//button[contains(@aria-label, 'Review your application')]",
        'success_message': "//h3[contains(text(), 'Application submitted')]",
        'job_title': "//h1[contains(@class, 'job-title')]"
    }
    
    # Environment variables (optional - for secure credential storage)
    @staticmethod
    def get_linkedin_email():
        return os.getenv('LINKEDIN_EMAIL', '')
    
    @staticmethod
    def get_linkedin_password():
        return os.getenv('LINKEDIN_PASSWORD', '')
    
    # Logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': LOG_FILE,
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
