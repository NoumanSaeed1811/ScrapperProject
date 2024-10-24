import csv
import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# In case you forgot how the plugin works check out this video :)

# https://www.youtube.com/watch?v=IgoIQutaVvg


# Make sure to have the following done:

# Python Installed

# Selenium Installed

# Chrome Driver Working

# Input your local user in the user_data_dir

# Login to Apollo on the user instance (run it one time to see if you're logged in or not, and if not, just log in)


# And then enjoy :)


chrome_options = Options()

user_data_dir = r'/home/nouman-saeed/.config/google-chrome/Default'

chrome_options.add_argument(f"user-data-dir={user_data_dir}")

chrome_driver_path = r'/home/nouman-saeed/PycharmProjects/Scrapper/chromedriver'

service = Service(chrome_driver_path)

driver = webdriver.Chrome(service=service, options=chrome_options)

# Link and name of CSV

driver.get("https://app.apollo.io/#/people?finderViewId=5b8050d050a3893c382e9360&contactLabelIds[]=67052612e12afd02d0dd51f4&page=1")

csv_file_name = '/home/nouman-saeed/PycharmProjects/Scrapper/Mix Odoo-Ma3-11.csv'

time.sleep(10)


def find_email_address(page_source):
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.findall(email_pattern, page_source)


def filter_emails(emails, excluded_domain):
    filtered = [email for email in emails if not email.endswith(excluded_domain)]
    return filtered[:2]


def split_name(name):
    parts = name.split()
    first_name = parts[0] if parts else ''
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
    return first_name, last_name
while True:
    try:
        loaded_section_selector = "[data-cy-loaded='true']"
        loaded_section = driver.find_element(By.CSS_SELECTOR, loaded_section_selector)

        tbodies = loaded_section.find_elements(By.TAG_NAME, 'tbody')
        if not tbodies:
            break

        for tbody in tbodies:
            try:
                first_anchor_text = tbody.find_element(By.TAG_NAME, 'a').text
                first_name, last_name = split_name(first_anchor_text)

                linkedin_url = ''
                for link in tbody.find_elements(By.TAG_NAME, 'a'):
                    href = link.get_attribute('href')
                    if 'linkedin.com' in href:
                        linkedin_url = href
                        break

                job_title_element = tbody.find_element(By.CLASS_NAME, 'zp_dqVxo')
                job_title = job_title_element.text if job_title_element else ''

                company_name = ''
                for link in tbody.find_elements(By.TAG_NAME, 'a'):
                    if 'accounts' in link.get_attribute('href'):
                        company_name = link.text
                        break

                phone_number = "'" + tbody.find_elements(By.TAG_NAME, 'a')[-1].text
                location_xpath = "./tr/td[6]"
                location_element = tbody.find_element(By.XPATH, location_xpath)
                location = location_element.text if location_element else ''
                city, country = location.split(', ') if ', ' in location else (location, '')

                button_classes = ["zp-button", "zp_GGHzP", "zp_m0QSL", "zp_Kbe5T", "zp_LOyEM", "zp_PLp2D", "zp_JDVxz"]

                button = tbody.find_element(By.CSS_SELECTOR, "." + ".".join(button_classes))
                if button:
                    button.click()
                    email_addresses = find_email_address(driver.page_source)
                    filtered_emails = filter_emails(email_addresses, 'sentry.io')
                    with open(csv_file_name, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        print(f"{first_name} has been poached!")
                        if len(filtered_emails) == 1:
                            writer.writerow(
                                [first_name, last_name, job_title, company_name, filtered_emails[0], '', linkedin_url,
                                phone_number, city, country])
                        elif len(filtered_emails) == 2:
                            writer.writerow(
                                [first_name, last_name, job_title, company_name, filtered_emails[0], filtered_emails[1],
                                linkedin_url, phone_number,city,country])
                    button.click()
                    tbody_height = driver.execute_script("return arguments[0].offsetHeight;", tbody)
                    driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", loaded_section, tbody_height)
            except NoSuchElementException:
                continue
            except TypeError:
                print("Type error occurred, moving to the next record.")
                continue

        # Pagination Logic
        next_button_selector = ".zp-button.zp_GGHzP.zp_PLp2D.zp_RY4qw[aria-label='right-arrow']"
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
            next_button.click()
            time.sleep(1)
        except NoSuchElementException:
            print("No more pages to navigate.")
            break

    except Exception as e:
        error_message = str(e)
        if "element click intercepted" in error_message:
            print("Your leads are ready!")
            break
        else:
            print(f"An error occurred: {error_message}")
            break

driver.quit()