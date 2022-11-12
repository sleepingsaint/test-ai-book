from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone 

class NeuralMagicBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

        options = Options()
        options.add_argument("--headless")
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(url)

        # declining cookies
        self.driver.find_element(By.ID, "hs-eu-decline-button").click()

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        title_tag = tag.find_element(By.CLASS_NAME, "entry-title")
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find_element(By.CLASS_NAME, "entry-title")
        a = title_tag.find_element(By.TAG_NAME, "a")
        return self.formatURL(a.get_attribute("href"))

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOn = tag.find_element(By.CLASS_NAME, "entry-date")
        return self.formatPublishedOn(publishedOn.text)


    def getAuthors(self, tag):
        if tag is None:
            return None

        return self.formatAuthors(None)

    def getTags(self, tag):
        if tag is None:
            return None

        return self.formatTags(None)

    @tryExceptNone
    def hasNextPage(self):
        pagination = self.driver.find_element(By.CLASS_NAME, "pagination")
        next_page_btn = pagination.find_element(By.CLASS_NAME, "nav-next-text")
        next_page_btn.click()
        return True 

    def getResources(self):
        prev = []
        while True:
            while True:
                try:
                    posts = self.driver.find_elements(By.CLASS_NAME, "post")
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
    title = "Neural Magic Blog"
    url = "https://neuralmagic.com/blog/"
    dateFormat = "%m/%d/%y"

    neuralmagicblog_client = NeuralMagicBlogClient(title, url, dateFormat)
    neuralmagicblog_client.getResources()
    neuralmagicblog_client.driver.close()