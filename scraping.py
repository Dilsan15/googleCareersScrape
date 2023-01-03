import time

import pandas as pd
import selenium.common
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class jobScraper:

    # On initialization, the class will be given the following parameters
    def __init__(self, basic_link, website_page, driver_path, links_needed, time_out, broswer_vis, timezone):

        self.links_needed = links_needed
        self.full_link = basic_link + website_page
        self.driver_path = driver_path
        self.time_out = time_out
        self.timezone = timezone
        self.bSoup = None

        self.link_stored = list()

        sel_service = Service(self.driver_path)
        option = webdriver.ChromeOptions()

        if not broswer_vis:
            option.add_argument("--headless")

        self.driver = webdriver.Chrome(service=sel_service, options=option)
        self.driver.get(f'{self.full_link}')
        self.getJobPostings()
        self.saveToCsv(self.getJobData())

    def getJobPostings(self):

        while len(self.link_stored) < self.links_needed:
            time.sleep(self.time_out)

            self.link_stored.extend(
                [hidLink.get_attribute("href") for hidLink in self.driver.find_elements(By.CLASS_NAME, "gc-card")])

            print(self.link_stored)

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                self.driver.find_element(By.XPATH,
                                         '//*[@id="jump-content"]/div[1]/div/div[2]/main/div/div[2]/div/div/div/a[2]').click()

            except selenium.common.ElementNotInteractableException:
                break

            print(str(len(self.link_stored)) + " / " + str(self.links_needed))
            self.link_stored = list(dict.fromkeys(self.link_stored))
            time.sleep(self.time_out)

        if len(self.link_stored) >= self.links_needed:
            self.link_stored = self.link_stored[:self.links_needed]

        print("final " + str(len(self.link_stored)) + "/" + str(self.links_needed))

    def getJobData(self):

        allJobData = list()

        for jobPost in self.link_stored:

            jobData = {}

            self.driver.get(jobPost)
            time.sleep(self.time_out)
            self.bSoup = bs(self.driver.page_source, 'html.parser')

            jobData["Title"] = self.bSoup.find("h1", {"class": "gc-card__title"}).text
            jobData["URL"] = self.driver.current_url

            """Google Careers is not consistent with how they display locations. Leaving this as a comment for now since
                is not 100 functioning
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

            jobData["Company"] = self.bSoup.find("span", itemprop="name").text

            try:
                job_qualifications = self.bSoup.find("div", itemprop="qualifications").findAll("ul")
                jobData["Min-Qualifications"] = job_qualifications[0].text
                jobData["Pref-Qualifications"] = job_qualifications[1].text

            except:
                jobData["Min-Qualifications"] = "N/A"
                jobData["Pref-Qualifications"] = "N/A"

            jobData["Description"] = self.bSoup.find("div", itemprop="description").text

            allJobData.append(jobData)
            print((str(self.link_stored.index(jobPost) + 1) + " / " + str(self.links_needed)))  # Indicates progress

        return allJobData


    def saveToCsv(self, data):
        """"Saves the data to a csv file and overwrites any previous data"""

        df = pd.DataFrame(data)
        df.to_csv('data/machineLearningJobData.csv', mode='w', index=False)
        print("Data Saved")
        print(df)
