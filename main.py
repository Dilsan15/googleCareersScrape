import os

from scraping import jobScraper

# Number of jobs need to be scraped. Google often only has less then 100 job postings for most roles
num_of_jobs_needed = 988

# Timezone
scraping_timezone = "MDT"

# Form website link
basic_link = "https://careers.google.com/"

# Link to a specific category
website_page = "jobs/results/?distance=50&q=Machine%20Learning"

# Path to the webdriver, saved as env
driver_path = os.environ["DRIVER_PATH"]  # Todo("CHANGE THIS TO UR PATH! so it looks like driver_path = 'YOUR STRING' ")

# time out needed between events, based on Wi-Fi and PC performance
time_out = 1.5

# Boolean which controls if the browser activities will be shown on screen on or not
browser_visible = True

if __name__ == "__main__":
    JobScraper = jobScraper(basic_link, website_page, driver_path, num_of_jobs_needed, time_out, browser_visible,
                            scraping_timezone)

"""Selenium was chosen as the web scraping tool as there was heavy javascript involved in the website to display the job 
postings. """
