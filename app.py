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

def initialize_driver():
    options = webdriver.ChromeOptions()

    # Add additional options to use the display created by Xvfb
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--display=:99")  # Set display to Xvfb

    return webdriver.Chrome(options=options)

# Calculate today's date and three days before
today_date = datetime.now().strftime('%Y-%m-%d')
three_days_before_date = (datetime.now() - timedelta(days=41)).strftime('%Y-%m-%d')

# Construct the modified website URL
website = f"https://www.sec.gov/edgar/search/?fbclid=IwAR0QhrfhVCRCfU8p1UERnZGgCvY0Mbydh9W0Oo4YTi4mQ3ti0Juhex6V71s#/q=Cybersecurity&dateRange=custom&category=custom&startdt={three_days_before_date}&enddt={today_date}&forms=8-K"

# Initialize the driver
with initialize_driver() as driver:
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

    def Summary():
        driver = initialize_driver()

        # Initialize a list to store overall_text for each URL
        overall_text_list = []

        # Initialize a list to store data for "Item 1.05"
        item_105_data = []

        for index, url in enumerate(link_visit):
            # Visit the URL
            driver.get(url)

            # Extract summ_elements
            summ_elements = driver.find_elements(By.XPATH, """(//*[self::p or self::span][contains(text(), 'On') and (contains(text(), 'January') or contains(text(), 'February') or contains(text(), 'March') or contains(text(), 'April') or contains(text(), 'May') or contains(text(), 'June') or contains(text(), 'July') or contains(text(), 'August') or contains(text(), 'September') or contains(text(), 'October') or contains(text(), 'November') or contains(text(), 'December'))])""")

            # Process summ_elements
            if len(summ_elements) > 1:
                # Concatenate texts if there are multiple summ_elements
                summary_text = ' '.join(element.text for element in summ_elements)
            elif len(summ_elements) == 1:
                # Get text if there is only one summ_elements
                summary_text = summ_elements[0].text
            else:
                # Handle the case where no summ_elements are found
                summary_text = "No summary found."

            # Extract the text content of the entire HTML
            overall_text = driver.find_element(By.TAG_NAME, 'body').text

            # Append the summary and overall_text to the lists
            summary.append(summary_text)
            overall_text_list.append(overall_text)
            # "item 1.05"
            # Check if "Item 1.05" is present in the HTML content
            if "item 1.05" in overall_text.lower():
                # Append data to the list for "Item 1.05"
                item_105_data.append({
                    'company_name': company_name[index],
                    'summary': summary_text,
                    'date_filed': date_filed[index],
                    'link_visit': link_visit[index]
                })

            time.sleep(1)

        driver.quit()

        # Convert the list of dictionaries to a DataFrame for "Item 1.05" data
        item_105_df = pd.DataFrame(item_105_data)

        # Check if the overall.csv exists, if not, create the directory and the file
        if not os.path.exists('data'):
            os.makedirs('data')

        overall_csv_path = 'data/overall.csv'
        if os.path.exists(overall_csv_path):
            overall_df = pd.read_csv(overall_csv_path)
            overall_df = pd.concat([overall_df, item_105_df], ignore_index=True)
        else:
            overall_df = item_105_df

        overall_df.to_csv(overall_csv_path, index=False)

    # Call the modified Summary function
    Summary()
