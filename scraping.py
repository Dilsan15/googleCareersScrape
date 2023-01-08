import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class jobScraper:

    # On initialization, the class will be given the following parameters
    def __init__(self, basic_link, website_page, driver_path, links_needed, time_out, broswer_vis, timezone):

        self.links_needed = links_needed
        self.time_out = time_out
        self.timezone = timezone

        self.link_stored = list()

        sel_service = Service(driver_path)
        option = webdriver.ChromeOptions()

        if not broswer_vis:
            option.add_argument("--headless")

        self.driver = webdriver.Chrome(service=sel_service, options=option)
        self.driver.get(f'{basic_link + website_page}')
        self.getJobPostings()
        self.saveToCsv(self.getJobData())

    def getJobPostings(self):
        """This function will scrape the website for the job postings and store them in a list"""
        while len(self.link_stored) < self.links_needed:
            time.sleep(self.time_out)

            # Find all the job postings on the page
            self.link_stored.extend(
                [hidLink.get_attribute("href") for hidLink in self.driver.find_elements(By.CLASS_NAME, "gc-card")])

            # Scroll down and Click the next button
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                self.driver.find_elements(By.CLASS_NAME,
                                          'gc-link--on-grey')[1].click()

            except:
                # Only occurs if we run out pages to scrape
                break

            # Remove any duplicate links
            self.link_stored = list(dict.fromkeys(self.link_stored))

            # Indicate progress
            print(str(len(self.link_stored)) + " / " + str(self.links_needed))

            time.sleep(self.time_out)

        if len(self.link_stored) >= self.links_needed:
            self.link_stored = self.link_stored[:self.links_needed]

        print("final " + str(len(self.link_stored)) + "/" + str(self.links_needed))

    def getJobData(self):
        """This function will scrape the list of job postings and store the data in a list of dictionaries"""
        allJobData = list()

        for jobPost in self.link_stored:

            jobData = {}

            self.driver.get(jobPost)
            time.sleep(self.time_out)
            bSoup = bs(self.driver.page_source, 'html.parser')

            jobData["Title"] = bSoup.find("h1", {"class": "gc-card__title"}).text
            jobData["Date-Scraped"] = f"{datetime.now()} {self.timezone}"
            jobData["URL"] = self.driver.current_url

            """Google Careers is not consistent with how they display locations. Leaving this as a comment for now since
                is not functioning 100% of the time. If we need this location data, I can try using a library to find locatoins 
                in the text
            """

            # try:
            #
            #     location_box = self.bSoup.find("p", {"class": "gc-job-detail__instruction-description"}).text
            #
            #     if "location" in location_box:
            #
            #         location_data = self.bSoup.find("p", {"class": "gc-job-detail__instruction-description"}).findAll(
            #             "b")
            #
            #         jobData["Office-Location"] = location_data[0].text.split(":")[1]
            #
            #         try:
            #             jobData["Remote-Location"] = location_data[1].text.split(":")[1]
            #         except:
            #             jobData["Remote-Location"] = "N/A"
            #
            #     else:
            #         raise Exception
            #
            # except:
            #     jobData["Office-Location"] = self.bSoup.find("div", itemprop="address").text
            #     jobData["Remote-Location"] = "N/A"

            jobData["Company"] = bSoup.find("span", itemprop="name").text

            # Try getting job qualification, if it fails, set the value to "N/A" as it does not exist

            try:
                job_qualifications = bSoup.find("div", itemprop="qualifications").findAll("ul")
                jobData["Min-Qualifications"] = job_qualifications[0].text
                jobData["Pref-Qualifications"] = job_qualifications[1].text

            except:
                jobData["Min-Qualifications"] = "N/A"
                jobData["Pref-Qualifications"] = "N/A"

            jobData["Description"] = bSoup.find("div", itemprop="description").text

            allJobData.append(jobData)
            print((str(self.link_stored.index(jobPost) + 1) + " / " + str(self.links_needed)))  # Indicates progress

        return allJobData

    def saveToCsv(self, data):
        """"Saves the data to a csv file and overwrites any previous data"""

        df = pd.DataFrame(data)
        df.to_csv('data/machineLearningJobData.csv', mode='w', index=False)
        print("Data Saved")
        print(df)
