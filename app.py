import os
import time
from selenium import webdriver
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException, TimeoutException
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Calculate today's date and three days before
today_date = datetime.now().strftime('%Y-%m-%d')
three_days_before_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')

# Construct the modified website URL
website = f"https://www.sec.gov/edgar/search/?fbclid=IwAR0QhrfhVCRCfU8p1UERnZGgCvY0Mbydh9W0Oo4YTi4mQ3ti0Juhex6V71s#/q=Cybersecurity&dateRange=custom&category=custom&startdt={three_days_before_date}&enddt={today_date}&forms=8-K"

# Open Chrome webdriver
driver = webdriver.Chrome()
time.sleep(5)
driver.get(website)
time.sleep(5)
link_visit = []
summary = []
company_name = []
date_filed = []

while True:
    try:
        time.sleep(10)

        # Scraping company_name and date_filed
        companys = driver.find_elements(By.XPATH, '//td[@class="entity-name"]')
        for company in companys:
            company_name.append(company.get_attribute('innerText'))

        dates = driver.find_elements(By.XPATH, '//td[@class="filed"]')
        for date in dates:
            date_filed.append(date.get_attribute('innerText'))

        # Wait until post_links are present in the DOM
        post_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//td[@class="filetype"]/a'))
        )

        for post_link in post_links:
            # Get the href attribute before clicking to handle the pop-up window
            # to_catch = post_link.get_attribute('href')

            # Click on the post link
            post_link.click()
            time.sleep(1)

            # Wait for the pop-up to appear
            to_catch = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[3]/a[1]'))
            ).get_attribute('href')

            # Do something with the 'to_catch' attribute (e.g., append it to a list)
            link_visit.append(to_catch)

            # Close the pop-up
            post_close_button = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/div[3]/button')
            post_close_button.click()

        # Find the next page link and click it
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div[2]/nav/ul/li[12]/a'))
        )
        time.sleep(5)
        next_page.click()

    except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, TimeoutException):
        # If the next page link is not found or any exception occurs, exit the loop
        break

driver.quit()

def Summary():
    # Use service account credentials from GitHub secrets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        eval(os.getenv('GOOGLE_SERVICE_ACCOUNT_CREDS')), scope)

    # Authorize with Google Sheets API
    client = gspread.authorize(creds)

    # Open the Google Sheets document
    sheet = client.open("Your Google Sheets Document Name").sheet1

    # Initialize a list to store data
    data = []

    for index in range(len(link_visit)):
        data.append([
            company_name[index],
            summary[index],
            date_filed[index],
            link_visit[index]
        ])

    # Clear the existing data in the sheet
    sheet.clear()

    # Append the new data to the sheet
    sheet.append_rows(data)

    print("Data uploaded to Google Sheets successfully!")

# Call the modified Summary function
Summary()
