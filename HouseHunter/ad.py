import HouseHunter.globals as Globals
from HouseHunter.helpers import Helpers

class WFPAd:
    # Note: Depending on supported origins, the current functionality may not apply to all, thus additional customization may be required.

    def __init__(self, origin, ad):
        self.origin = origin
        self.parent = ad.find('div', {"class": "home-information"})
        self.title = self.parent.find('h2').text.strip()
        self.id = self.title
        self.ad = ad
        self.info = {}

        self.__locate_info()
        self.__parse_info()

    def __locate_info(self):
        # Locate ad information
        self.info["Title"] = self.title
        self.info["Image"] = self.parent.find("div", {"class": "photo-container"}).find("img")['src']
        self.info["Url"] = self.parent.find("div", {"class": "photo-container"}).find("a", href=True)['href']
        self.info["Description"] = self.parent.find(lambda tag:tag.name=="p" and "|" in tag.text)
        self.info["Location"] = self.parent.find('p', {"class": "neigh"})
        self.info["Price"] = self.parent.find('p', {"class": "price"})

    def __parse_info(self):
        # Parse remaining ad information
        for key, value in self.info.items():
            if value:
                if key == "Url":
                    self.info[key] = Globals.SUPPORTED_ORIGINS[self.origin] + value

                elif key == "Description" or key == "Location" or key == "Price":
                    self.info[key] = Helpers.removeHTMLTags(str(value))

                if key == "Image":
                    self.info[key] = 'https:' + value
                    
class RewAd():
    # Note: Depending on supported origins, the current functionality may not apply to all, thus additional customization may be required.

    def __init__(self, origin, ad):
        self.origin = origin
        self.parent = ad.find('div', {"class": "displaypanel-wrapper"})
        self.title = self.parent.find('div', {"class": "displaypanel-body"}).find('a')["title"].strip()
        self.id = self.title
        self.ad = ad
        self.info = {}

        self.__locate_info()
        self.__parse_info()

        print(self.info)

    def __locate_info(self):
        # Locate ad information
        self.info["Title"] = self.title
        self.info["Image"] = self.parent.find("img")['src']
        self.info["Url"] = self.parent.find('div', {"class": "displaypanel-body"}).find('a')["href"]
        self.info["Description"] = self.parent.find(lambda tag:tag.name=="li" and " bd" in tag.text).text + " " +  self.parent.find(lambda tag:tag.name=="li" and " ba" in tag.text).text + " " + self.parent.find(lambda tag:tag.name=="li" and "sf" in tag.text).text
        self.info["Location"] = self.title
        self.info["Price"] = self.parent.find('div', {"class": "displaypanel-title"}).text

    def __parse_info(self):
        # Parse remaining ad information
        for key, value in self.info.items():
            if value:
                if key == "Url":
                    self.info[key] = Globals.SUPPORTED_ORIGINS[self.origin] + value

                elif key == "Description" or key == "Location" or key == "Price":
                    self.info[key] = Helpers.removeHTMLTags(str(value))
