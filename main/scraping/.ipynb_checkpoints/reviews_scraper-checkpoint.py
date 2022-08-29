#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Corentin Werenne
"""

# Imports
import requests #For requesting html
import re #For regular expressions
import time
import pandas as pd
import random
import datetime

# Get credentials
f = open('credentials.txt', 'r') #Opens the credentials.txt file for reading
credentials = f.readlines() #Returns a list of strings with cookie and 

# Setup
payload = ""
headers = {
    'cookie': credentials[0].replace('\n', ''),
    'authority': "www.glassdoor.com",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'accept-language': "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    'cache-control': "max-age=0",
    'referer': "https://nl.glassdoor.be/",
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    'sec-ch-ua-mobile': "?0",
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': "document",
    'sec-fetch-mode': "navigate",
    'sec-fetch-site': "same-origin",
    'sec-fetch-user': "?1",
    'upgrade-insecure-requests': "1",
    'user-agent': credentials[1].replace('\n', '')
    }

# Get responses
def get_response(url):
    """
    returns glassdoor review query for a url converted to raw string
    """
    response = requests.request("GET", url, data=payload, headers=headers)
    raw_response = repr(response.text)
    return raw_response




review_pattern = re.compile(r'{\"__typename\":\"EmployerReview\".+?\"translationMethod\":.+?}')
def get_reviews(response):
    matches = review_pattern.finditer(response)
    reviews = []
    for i, match in enumerate(matches):
        reviews.append(match.group(0))
    return reviews



def extract_from_review(review):
    """
    Expects a review build like a string dictionnary, returns a proper dictionary
    """
    review_id = re.compile(r'\"reviewId\":(\d+?),\"reviewDateTime"').search(review).group(1)
    review_datetime = re.compile(r'\"reviewDateTime\":\"(.+?)\",\"ratingOverall\"').search(review).group(1)
    rating_overall = re.compile(r'\"ratingOverall\":([0-5]),\"ratingCeo\"').search(review).group(1)
    rating_ceo = re.compile(r'\"ratingCeo\":(.+?),\"ratingBusinessOutlook\"').search(review).group(1)
    rating_businessoutlook = re.compile(r'\"ratingBusinessOutlook\":(.+?),\"ratingWorkLifeBalance\"').search(review).group(1)
    rating_worklife_balance = re.compile(r'\"ratingWorkLifeBalance\":([0-5]),\"ratingCultureAndValues\"').search(review).group(1)
    rating_culture_values = re.compile(r'\"ratingCultureAndValues\":([0-5]),\"ratingDiversityAndInclusion\"').search(review).group(1)
    rating_diversity_inclusion = re.compile(r'\"ratingDiversityAndInclusion\":([0-5]),\"ratingSeniorLeadership\"').search(review).group(1)
    rating_senior_leadership = re.compile(r'\"ratingSeniorLeadership\":([0-5]),\"ratingRecommendToFriend\"').search(review).group(1)
    rating_recommend_friend = re.compile(r'\"ratingRecommendToFriend\":(.+?),\"ratingCareerOpportunities\"').search(review).group(1)
    rating_career_opport = re.compile(r'\"ratingCareerOpportunities\":([0-5]),\"ratingCompensationAndBenefits\"').search(review).group(1)
    rating_compensation_benefits = re.compile(r'\"ratingCompensationAndBenefits\":([0-5]),\"employer\"').search(review).group(1)
    is_current_job = re.compile(r'\"isCurrentJob\":([a-z]+),\"lengthOfEmployment\"').search(review).group(1)
    length_employment = re.compile(r'\"lengthOfEmployment\":(\d+),\"employmentStatus\"').search(review).group(1)
    employment_status = re.compile(r'"employmentStatus":(.+?),"jobEndingYear"').search(review).group(1)
    # Probably needs adjustement when a year is provided
    job_ending_year = re.compile(r'"jobEndingYear":(.+?),"jobTitle"').search(review).group(1)
    pros = re.compile(r'\"pros\":\"(.+?)\",\"prosOriginal\":').search(review).group(1)
    cons = re.compile(r'\"cons\":\"(.+?)\",\"consOriginal\":').search(review).group(1)
    advice = re.compile(r'\"advice\":(.+?),\"adviceOriginal\":').search(review).group(1)
    count_helpful = re.compile(r'\"countHelpful\":(\d+),\"countNotHelpful\":').search(review).group(1)
    count_nothelpful = re.compile(r'\"countNotHelpful\":(\d+),\"employerResponses\"').search(review).group(1)
    employer_reponses = re.compile(r'\"employerResponses\":(.+?),\"featured\"').search(review).group(1)
    language_id = re.compile(r'\"languageId\":(.+?),\"translationMethod\"').search(review).group(1)
    post_title = re.compile(r'\"summary\":(.+?),\"summaryOriginal\"').search(review).group(1)

    
    review_data = {'review_id': review_id,
               'post_title': post_title,
               'review_datetime': review_datetime,
               'review_overall': rating_overall,
               'rating_ceo': rating_ceo,
               'rating_businessoutlook': rating_businessoutlook,
               'rating_worklifebalance': rating_worklife_balance,
               'rating_culture_values': rating_culture_values,
               'rating_diversity_inclusion': rating_diversity_inclusion,
               'rating_senior_leadership': rating_senior_leadership,
               'rating_recommend_friend': rating_recommend_friend,
               'rating_career_opport': rating_career_opport,
               'rating_compensation_benefits': rating_compensation_benefits,
               'is_current_job': is_current_job,
               'length_employment': length_employment,
               'employment_status': employment_status,
               'job_ending_year': job_ending_year,
               'pros': pros,
               'cons': cons,
               'advice': advice,
               'count_helpful': count_helpful,
               'count_nothelpful': count_nothelpful,
               'employer_reponses': employer_reponses,
               'language_id': language_id}
    
    return review_data

def datestr_to_str(date_str):
    """
    Convert a string with format 2022-06-13T05:07:07.813 to a datetime object
    """
    t_index = date_str.index('T')
    date = date_str[:t_index]
    date_time = datetime.datetime.strptime(date, '%Y-%m-%d')
    return date_time
    

def url_to_df(url, max_date, filter_path, s):
    """

    Parameters
    ----------
    url : str
        Base url with no filter except maybe location.
        ex: 'https://www.glassdoor.com/Reviews/Deloitte-Reviews-E2763.htm'
    max_date : string
        Defines how far the scraper will go in the past. 
        WARNING: This features only works properly if sorted by most recent
        ex: '2022-05-09'
    filter_path : str
        Add a filter to the reviews like job type, language or sorted by most recent.
        ex: '?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME&filter.employmentStatus=INTERN'
    s : int
        Defines how much pause between each request to the server. The lower the faster
        but also the more at risk of getting banned.
        

    Returns
    -------
    A list of dictionaries containing the information extracted from the reviews.

    """
    # Pattern to extract the reviews out of the javascript response
    review_pattern = re.compile(r'{\"__typename\":\"EmployerReview\".+?\"translationMethod\":.+?}')
    
    # Transform string date into datetime object for comparison
    max_date = datetime.datetime.strptime(max_date, '%Y-%m-%d')
    
    reviews_parsed = []
    htm_index = url.index('.htm')
    page = 1
    
    urlp = url[:htm_index] + '_P' + str(page) + '.htm' + filter_path 
    response = get_response(urlp)
    reviews = get_reviews(response)
    for review in reviews:
        reviews_parsed.append(extract_from_review(review))
    latest_date = reviews_parsed[-1]['review_datetime']
    time.sleep(random.uniform(s-1, s+1))

    while datestr_to_str(latest_date) > max_date:
        page +=1
        urlp = url[:htm_index] + '_P' + str(page) + '.htm' + filter_path 
        print(urlp)
        response = get_response(urlp)
        reviews = get_reviews(response)
        for review in reviews:
            reviews_parsed.append(extract_from_review(review))
        latest_date = reviews_parsed[-1]['review_datetime']
        print(latest_date)
        time.sleep(random.uniform(s-1, s+1))
        if page % 100 == 0:
            pd.DataFrame(reviews_parsed[:-2]).to_csv(f'../../data/rev_{page}.csv')
            reviews_parsed = []
            time.sleep(random.uniform(90, 110))
        else: 
            continue
        
        
    return reviews_parsed

reviews_df = url_to_df('https://www.glassdoor.com/Reviews/Deloitte-Reviews-E2763.htm',
                       '2022-03-15',
                       '?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME&filter.employmentStatus=INTERN',
                       6)
