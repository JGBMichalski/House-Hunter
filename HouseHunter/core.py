from tarfile import SUPPORTED_TYPES
import requests
import re
from bs4 import BeautifulSoup
import json
import HouseHunter.globals as Globals
from HouseHunter.ad import *
from pathlib import Path

class Core():

    def __init__(self, filename="ads.json"):
        self.filepath = Path().absolute().joinpath(filename) if filename else None
        self.all_ads = {}
        self.new_ads = {}

        self.third_party_ads = []

        self.load_ads()

    # Reads given file and creates a dict of ads in file
    def load_ads(self):
        # If filepath is None, just skip local file
        if self.filepath:
            # If the file doesn't exist create it
            if not self.filepath.exists():
                ads_file = self.filepath.open(mode='w')
                ads_file.write("{}")
                ads_file.close()
                return

            with self.filepath.open(mode="r") as ads_file:
                self.all_ads = json.load(ads_file)

    # Save ads to file
    def save_ads(self):
        # If filepath is None, just skip local file
        if self.filepath:
            with self.filepath.open(mode="w") as ads_file:
                json.dump(self.all_ads, ads_file)

    def validate_origin(self, url):
        for origin in Globals.SUPPORTED_ORIGINS:
            if origin in url:
                return Globals.SUPPORTED_ORIGINS.index(origin)
        return -1


    # Pulls page data from a given url and finds all ads on each page
    def scrape_url_for_ads(self, url):
        self.new_ads = {}
        email_title = None
        origin = self.validate_origin(url)

        if origin < 0:
            print("Site not supported: {}".format(url))
            return self.new_ads, email_title

        while url:           
            # Get the html data from the URL
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            # If the email title doesnt exist pull it from the html data
            if email_title is None:
                email_title = self.get_email_title(origin, soup)

            # Find ads on the page
            self.find_ads(soup, origin)

            # Set url for next page of ads 
            # Depending on supported origins, this may not apply to all
            
            url = soup.find("a", string="Next")

            if not url:
                url = soup.find("a", href=True, rel="next")

            if url:
                url = Globals.SUPPORTED_ORIGINS[origin] + url['href']

        return self.new_ads, email_title

    def find_ads(self, soup, origin):
        # Finds all ad trees in page html.
        ad_regex = re.compile('.*{}.*'.format(Globals.AD_ROOT_CLASS_NAMES[origin][Globals.PRIMARY]))
        ads = soup.find_all(Globals.AD_ROOT_ELEMENT_TYPE[origin], {"class": ad_regex})

        # If no ads use different class name
        if not ads:
            ad_regex = re.compile('.*{}.*'.format(Globals.AD_ROOT_CLASS_NAMES[origin][Globals.SECONDARY]))
            ads = soup.find_all(Globals.AD_ROOT_ELEMENT_TYPE[origin], {"class": ad_regex})

        # Create a dictionary of all ads with ad id being the key
        for ad in ads:
            if origin == 0:
                current_ad = WFPAd(origin, ad)
            elif origin == 1:
                current_ad = RewAd(origin, ad)
            else:
                return

            # Skip third-party ads and ads already found
            if (current_ad.id not in self.all_ads):
                self.new_ads[current_ad.id] = current_ad.info
                self.all_ads[current_ad.id] = current_ad.info

    def get_email_title(self, origin, soup):
        if origin != 0: 
            # Used for origins that do not give any details about the search options
            return Globals.SUPPORTED_FULL_NAMES[origin]
        else:
            # Depending on supported origins, this may not apply to all
            email_title_location = soup.find('div', {"class": "results-info"}).find('h1')

            if email_title_location:
                # Depending on supported origins, this may not apply to all
                return self.format_title(email_title_location.text.split(' in ')[1].strip('"'))
            else: 
                return ""


    # Makes the first letter of every word upper-case
    def format_title(self, title):
        new_title = []

        title = title.split()
        for word in title:
            new_word = ''
            new_word += word[0].upper()

            if len(word) > 1:
                new_word += word[1:]

            new_title.append(new_word)

        return ' '.join(new_title)

    # Returns a given list of words to lower-case words
    def words_to_lower(self, words):
        return [word.lower() for word in words]
