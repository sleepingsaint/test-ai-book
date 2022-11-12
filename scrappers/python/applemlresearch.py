from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone, tryExceptFalse

class AppleMLResearchBlogClient(AIBookClient):
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
        title_tag = tag.find_element(By.CLASS_NAME, "post-title")
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find_element(By.CLASS_NAME, "post-title")
        a = title_tag.find_element(By.TAG_NAME, "a")
        return self.formatURL(a.get_attribute("href"))

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None
        return None

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        authors = tag.find_elements(By.TAG_NAME, "div")[-1]
        return self.formatAuthors(authors.text.replace("Authors", "").split(","))

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        meta_container = tag.find_element(By.CLASS_NAME, "tag-header")
        tags = []
        
        try:
            tag_type = meta_container.find_element(By.CLASS_NAME, "tag-type")
            tags.append(tag_type.text.capitalize().strip())
        except:
            pass
        
        try:
            domain_tag = meta_container.find_element(By.CLASS_NAME, "tag-domain")
            domain = domain_tag.text.replace("research area", "")
            tags.append(domain.strip())
        except:
            pass
    
        try:
            conference_tag = meta_container.find("a", {"class": "tag-conference"})
            conference = conference_tag.text.replace("conference", "")
            year = meta_container.find("a", {"class": "tag-year"}).text.replace("Published year", "")
            tags.append(f"{conference} {year}")
        except:
            pass

        return self.formatTags(tags)

    @tryExceptFalse
    def hasNextPage(self):
        pagination = self.driver.find_element(By.CLASS_NAME, "pagination")
        next_page_btn = pagination.find_element(By.CLASS_NAME, "paddlenav-arrow-next")
        next_page_btn.click()
        return True 

    def getResources(self):
        prev = []
        while True:
            while True:
                try:
                    container = self.driver.find_element(By.CLASS_NAME, "article-list")
                    posts = container.find_elements(By.TAG_NAME, "li")
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
    title = "Apple ML Research Blog"
    url = "https://machinelearning.apple.com/research"
    dateFormat = "%Y"

    applemlresearchblog_client = AppleMLResearchBlogClient(title, url, dateFormat)
    applemlresearchblog_client.getResources()
    applemlresearchblog_client.driver.close()