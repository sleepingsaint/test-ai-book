from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone, tryExceptFalse

class MarkTechPostClient(AIBookClient):
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

        h3 = tag.find_element(By.TAG_NAME, "h3")
        a = h3.find_element(By.TAG_NAME, "a")
        return self.formatTitle(a.get_attribute("title"))
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None

        h3 = tag.find_element(By.TAG_NAME, "h3")
        a = h3.find_element(By.TAG_NAME, "a")
        return self.formatURL(a.get_attribute("href"))
    
    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None
        span = tag.find_element(By.CLASS_NAME, "td-post-author-name")
        a = span.find_element(By.TAG_NAME, "a")
        return self.formatAuthors(a.text)
    
    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None
        span = tag.find_element(By.CLASS_NAME, "td-post-date")
        return self.formatPublishedOn(span.text)

    @tryExceptNone
    def getTags(self, tag=None):
        if tag is None:
            return self.formatTags(None)
        return self.formatTags(None) 

    @tryExceptFalse
    def hasNextPage(self):
        next_page_btn = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label='next-page']")
        next_page_btn.click()
        return True

    def getResources(self, prev=[]):
        while True:
            try:
                posts = self.driver.find_elements(By.CLASS_NAME, "td-block-span4")
                if posts != prev:
                    break
            except NoSuchElementException:
                pass

        for post in posts:
            title = self.getTitle(post)
            url = self.getURL(post)
            
            if title is None or url is None:
                continue

            authors = self.getAuthors(post)
            publishedOn = self.getPublishedOn(post)
            tags = self.getTags(None)

            if not self.handleResource(title, url, authors, tags, publishedOn):
                return

        if self.hasNextPage():
            self.getResources(posts)

if __name__ == "__main__":
    title = "MarkTechPost"
    url = "https://www.marktechpost.com/category/technology/"
    dateFormat = "%B %d, %Y"

    markTechPost_client = MarkTechPostClient(title, url, dateFormat)
    markTechPost_client.getResources()