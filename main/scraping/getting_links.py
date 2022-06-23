# -*- coding: utf-8 -*-
"""
Script to get links of review pages on glassdoor for a list of companies. 
You can eventually add filters such as location, job type, language etc.

Author: Corentin Werenne
"""
# Imports
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, WebDriverException

import logging
import re
import random
import time
# import pandas as pd


# Create and configure logger
logging.basicConfig(filename='getting_links.log',
                    level=logging.INFO, # Lowest level, to see all levels
                    force=True,
                    format='%(levelname)s %(asctime)s - %(message)s') # w for overwriting the log file each time, default is just appending
logger=logging.getLogger()


# Setup functions
# Getting rid of overlay function
def get_rid_overlay(driver):
    """
    Sometimes the site shows an overlay that cannot be removed by clicking, 
    this blocks interaction with the site.
    This is some code to remove it.
    """
    
    driver.execute_script("""
        javascript:(function(){
          document.getElementsByClassName('hardsellOverlay')[0].remove();
          document.getElementsByTagName("body")[0].style.overflow = "scroll";
          let style = document.createElement('style');
          style.innerHTML = `
            #LoginModal {
              display: none!important;
            }
          `;
          document.head.appendChild(style);
          window.addEventListener("scroll", function (event) {
            event.stopPropagation();
          }, true);
        })();
        """)
    return driver

# Launches driver and goes on company search bar
def setup_driver_to_reviews_search():
    """
    Launches driver, sets window size and implicit wait
    """
    driver = webdriver.Chrome('/Users/corentin/OneDrive - Universite de Liege/chromedriver_2')
    time.sleep(3)
    driver.set_window_size(1280, 800)
    driver.implicitly_wait(20)
    driver.get('https://www.glassdoor.com/Reviews/index.htm')
    logger.info('Driver launched and intialized on glassdoor.com')
    return driver

# Set site language to us
def set_site_language(driver):
    """
    Sets setting of the site to united state
    """
    time.sleep(random.uniform(2, 4))
    # Scroll to the bottom of the page
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(random.uniform(2, 4))
    
    # Find the box for language choice and click on it
    language_choice = driver.find_element_by_xpath('//*[@id="Footer"]/nav/ul[2]/li[3]/div/div/div[1]')
    language_choice.click()
    
    # Parse the html of the page and find the choices of language, click on united states
    soup = BeautifulSoup(driver.page_source, 'lxml')
    language_click_box = soup.find('div', 
                                   class_='dropdownOptions dropdownExpanded animated above')
    for li in language_click_box.find_all('li'):
        country = li.find_all('span')[1].string
        if country == 'United States':
            us_id = li.get('id')
            break
    us = driver.find_element_by_id(us_id)
    time.sleep(random.uniform(2, 4))
    us.click()
    time.sleep(random.uniform(2, 4))
    logger.info('Language succesfully changed to English')
    
    return driver


# Getting reviews urls functions
# Searching for the company on glassdoor
def search_company(company, driver):
    """
    Searches the name of a company in the search bar
    """
    driver.get('https://www.glassdoor.com/Reviews/index.htm')
    time.sleep(random.uniform(2, 4))
    search_bar = driver.find_element_by_xpath('//*[@id="KeywordSearch"]')
    time.sleep(random.uniform(2, 4))
    search_bar.send_keys(company)
    time.sleep(random.uniform(2, 4))
    search_bar.send_keys(Keys.ENTER)
    time.sleep(random.uniform(2, 4))
    
    try:
        first_result = driver.find_element_by_xpath('//*[@id="MainCol"]/div/div[1]/div/div[1]/div/div[2]/h2/a')
        first_result.click()
        logger.info(f'Found result for {company}')
    except:
        logger.info(f'DID NOT find result for {company}')
        
    return driver

# Getting the review_page
def get_reviews_page(driver):
    """
    A company page has multiple components, we want to get the reviews page
    """
    soup = BeautifulSoup(driver.page_source, 'lxml')
    reviews_tag = soup.find('a', {'data-test': 'reviewSeeAllLink'})
    url_path = reviews_tag.get('href')
    domain = 'https://www.glassdoor.com'
    reviews_url = domain + url_path
    
    driver.get(reviews_url)
    logger.info('Succesfully got reviews page')
    
    return driver

# Specifying the locations
def get_url_by_location(locations, driver):
    """
    Adjusts window size because otherwise no scrolling possible
    Selects a location and returns url of the page
    """
    driver.set_window_size(1384, 789)
    time.sleep(random.uniform(2, 4))
    
    urls = {}
    for location in locations:
        try:
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollBy(0, arguments[0]);", 500)
    
            filter_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[2]/button/span')
            filter_button.click()
            time.sleep(random.uniform(2, 3))
    
            location_box = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]')
            location_box.click()
            time.sleep(random.uniform(2, 3))
    
            location_input = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/div/div/div/input')
            location_input.send_keys(location)
            time.sleep(random.uniform(1, 2))
            location_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(random.uniform(1, 2))
            location_input.send_keys(Keys.ENTER)
    
            time.sleep(random.uniform(2, 4))
            urls[location] = driver.current_url
            logger.info(f'url for {location} is {urls[location]}')
        except:
            driver = get_rid_overlay(driver)
            
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollBy(0, arguments[0]);", 500)
    
            filter_button = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[2]/div[2]/button/span')
            filter_button.click()
            time.sleep(random.uniform(2, 3))
    
            location_box = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]')
            location_box.click()
            time.sleep(random.uniform(2, 3))
    
            location_input = driver.find_element_by_xpath('//*[@id="MainContent"]/div/div[1]/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/div/div/div/input')
            location_input.send_keys(location)
            time.sleep(random.uniform(1, 2))
            location_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(random.uniform(1, 2))
            location_input.send_keys(Keys.ENTER)
    
            time.sleep(random.uniform(2, 4))
            urls[location] = driver.current_url
            logger.info(f'url for {location} is {urls[location]}')
            
    return driver, urls

# Add filters
def add_filter(urls, filter_path):
    """
    You can use this function to alter the link if you want to change the language 
    or the job types (intern, full time, etc)
    """
    general_url = re.compile(r'(https://www\.glassdoor\.com.+?\.htm)\?filter')
    for key, value in urls.items():
        raw_url = general_url.search(repr(urls[key])).group(1)
        logger.info(f'raw_url for {key} is {raw_url}')
        filtered_url = raw_url + filter_path
        urls[key] = filtered_url
        logger.info(f'url_filtered for {key} is {filtered_url}')
        
    return urls

def get_urls(companies, locations, filter_path):
    """
    
    Parameters
    ----------
    companies : TYPE
        DESCRIPTION.
    locations : TYPE
        DESCRIPTION.
    filter_path : TYPE
        DESCRIPTION.

    Returns
    -------
    company_urls : TYPE
        DESCRIPTION.

    """
    
    # Setup driver
    driver = setup_driver_to_reviews_search()
    
    # Changes language site to english
    driver = set_site_language(driver)
    
    # Gets urls
    company_urls = {}
    for company in companies:
        driver = search_company(company, driver)
        time.sleep(random.uniform(2, 4))
        driver = get_reviews_page(driver)
        time.sleep(random.uniform(3, 4))

        driver, urls = get_url_by_location(locations, driver)

        urls = add_filter(urls, filter_path)
        print(urls)
        company_urls[company] = urls
        
        
    return company_urls

company_urls = get_urls(['pwc', 'deloitte'], ['belgium', 'netherlands'], '?filter.iso3Language=eng&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME&filter.employmentStatus=INTERN')








