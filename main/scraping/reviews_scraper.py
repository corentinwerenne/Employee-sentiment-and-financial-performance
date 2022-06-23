#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Corentin Werenne
"""

# Imports
import requests #For requesting html
from bs4 import BeautifulSoup #For parsing html
import js2py #Transforming javascript code into a dictionary type object
import re #For regular expressions
import codecs #To convert raw strings to normal ones
import json #To convert a string to a dictionary
import time

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

response = get_response('https://www.glassdoor.com/Reviews/Deloitte-Reviews-E2763.htm')


review_pattern = re.compile(r'{\"__typename\":\"EmployerReview\".+?\"translationMethod\":.+?}')
def get_reviews(response):
    matches = review_pattern.finditer(response)
    reviews = []
    for i, match in enumerate(matches):
        reviews.append(match.group(0))
    return reviews

reviews = get_reviews(response)

def extract_from_review(review):
    """
    Expects a review build like a string dictionnary, returns a proper dictionary
    """
    review_id = re.compile(r'\"reviewId\":(\d+?),\"reviewDateTime"').search(review).group(1)
    review_datetime = re.compile(r'\"reviewDateTime\":\"(.+?)\",\"ratingOverall\"').search(review).group(1)
    rating_overall = re.compile(r'\"ratingOverall\":([0-5]),\"ratingCeo\"').search(review).group(1)
    rating_ceo = re.compile(r'\"ratingCeo\":\"([A-Z]+)\",\"ratingBusinessOutlook\"').search(review).group(1)
    rating_businessoutlook = re.compile(r'\"ratingBusinessOutlook\":\"([A-Z]+)\",\"ratingWorkLifeBalance\"').search(review).group(1)
    rating_worklife_balance = re.compile(r'\"ratingWorkLifeBalance\":([0-5]),\"ratingCultureAndValues\"').search(review).group(1)
    rating_culture_values = re.compile(r'\"ratingCultureAndValues\":([0-5]),\"ratingDiversityAndInclusion\"').search(review).group(1)
    rating_diversity_inclusion = re.compile(r'\"ratingDiversityAndInclusion\":([0-5]),\"ratingSeniorLeadership\"').search(review).group(1)
    rating_senior_leadership = re.compile(r'\"ratingSeniorLeadership\":([0-5]),\"ratingRecommendToFriend\"').search(review).group(1)
    rating_recommend_friend = re.compile(r'\"ratingRecommendToFriend\":\"([A-Z]+)\",\"ratingCareerOpportunities\"').search(review).group(1)
    rating_career_opport = re.compile(r'\"ratingCareerOpportunities\":([0-5]),\"ratingCompensationAndBenefits\"').search(review).group(1)
    rating_compensation_benefits = re.compile(r'\"ratingCompensationAndBenefits\":([0-5]),\"employer\"').search(review).group(1)
    is_current_job = re.compile(r'\"isCurrentJob\":([a-z]+),\"lengthOfEmployment\"').search(review).group(1)
    length_employment = re.compile(r'\"lengthOfEmployment\":(\d+),\"employmentStatus\"').search(review).group(1)
    employment_status = re.compile(r'"employmentStatus":\"([A-Z]+)\","jobEndingYear"').search(review).group(1)
    # Probably needs adjustement when a year is provided
    job_ending_year = re.compile(r'"jobEndingYear":([a-z]+),"jobTitle"').search(review).group(1)
    pros = re.compile(r'\"pros\":\"(.+?)\",\"prosOriginal\":').search(review).group(1)
    cons = re.compile(r'\"cons\":\"(.+?)\",\"consOriginal\":').search(review).group(1)
    advice = re.compile(r'\"advice\":(.+?),\"adviceOriginal\":').search(review).group(1)
    count_helpful = re.compile(r'\"countHelpful\":(\d+),\"countNotHelpful\":').search(review).group(1)
    count_nothelpful = re.compile(r'\"countNotHelpful\":(\d+),\"employerResponses\"').search(review).group(1)
    employer_reponses = re.compile(r'\"employerResponses\":(.+?),\"featured\"').search(review).group(1)
    review_id = re.compile(r'\"languageId\":\"([a-z]+)\",\"translationMethod\"').search(review).group(1)
    # review_id = re.compile(r'\"reviewId\":(\d+?),').search(review).group(1)
    # review_id = re.compile(r'\"reviewId\":(\d+?),').search(review).group(1)
    # review_id = re.compile(r'\"reviewId\":(\d+?),').search(review).group(1)
    # review_id = re.compile(r'\"reviewId\":(\d+?),').search(review).group(1)
    # review_id = re.compile(r'\"reviewId\":(\d+?),').search(review).group(1)
    # review_id = re.compile(r'\"reviewId\":(\d+?),').search(review).group(1)
    
    review_data = {'review_id': review_id,
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
               'review_id': review_id}
    
    return review_data

extract_from_review(response)