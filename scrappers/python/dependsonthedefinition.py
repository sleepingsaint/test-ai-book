from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone 

class DependsOnTheDefinitionClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

        options = Options()
        options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(url)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        title_tag = tag.find_element(By.CLASS_NAME, "title")
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find_element(By.CLASS_NAME, "title")
        a = title_tag.find_element(By.TAG_NAME, "a")
        return self.formatURL(a.get_attribute("href"))

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOn = tag.find_element(By.CLASS_NAME, "date")
        return self.formatPublishedOn(publishedOn.text)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        return self.formatAuthors(None)

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        tags = []
        tags_container = tag.find_element(By.CLASS_NAME, "tags")
        tag_elements = tags_container.find_elements(By.TAG_NAME, "a")
        for ele in tag_elements:
            tags.append(ele.text.replace("#", "").capitalize().strip())
        return self.formatTags(tags)

    @tryExceptNone
    def hasNextPage(self):
        container = self.driver.find_element(By.CLASS_NAME, "level-right")
        nextPageURL = container.find_element(By.TAG_NAME, "a").get_attribute("href")
        self.driver.get(nextPageURL)
        return True 

    def getResources(self):
        prev = []
        while True:
            while True:
                try:
                    posts = self.driver.find_elements(By.TAG_NAME, "article")
                    if len(posts) > 0 and posts != prev:
                        break
                except:
                    pass

            for post in posts:
                title = self.getTitle(post)
                url = self.getURL(post)
                
                if title is None or url is None:
                    continue
                
                authors = self.getAuthors(post)
                publishedOn = self.getPublishedOn(post)
                tags = self.getTags(post)

                if not self.handleResource(title, url, authors, tags, publishedOn):
                    return

            if not self.hasNextPage():
                break
            prev = posts

if __name__ == "__main__":
    title = "Depends On The Definition Blog"
    url = "https://www.depends-on-the-definition.com/"
    dateFormat = "%B %d, %Y"

    dependsonthedefinition_client = DependsOnTheDefinitionClient(title, url, dateFormat)
    dependsonthedefinition_client.getResources()
    dependsonthedefinition_client.driver.close()