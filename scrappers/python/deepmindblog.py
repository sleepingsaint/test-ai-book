import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone 

class DeepmindBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)
        
        options = Options()
        options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(url)

        # removing the cookie btn
        cookie_bar_btn = self.driver.find_element(By.CLASS_NAME, "cookieBarConsentButton")
        cookie_bar_btn.click()

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
        return self.formatAuthors(a.text.split(','))
    
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

    @tryExceptNone
    def hasNextPage(self):
        self.driver.find_element(By.CLASS_NAME, "w-pagination-next").click()
        return True 
    
    def getBannerPost(self):
        banner_post = self.driver.find_element(By.CLASS_NAME, "c_banner__blog__card")

        title = banner_post.find_element(By.CLASS_NAME, "c_banner__blog__card__title").text
        tags = banner_post.find_element(By.CLASS_NAME, "c_banner__blog__card__category").text
        publishedOn = banner_post.find_element(By.CLASS_NAME, "c_banner__blog__card__meta").text
        url = banner_post.find_element(By.CLASS_NAME, "c_banner__blog__card__link").get_attribute('href')

        title = self.formatTitle(title)
        url = self.formatURL(url)

        if title is None or url is None:
            return

        authors = self.formatAuthors(None)
        publishedOn = self.formatPublishedOn(publishedOn)
        tags = self.formatTags(tags)

        if not self.handleResource(title, url, authors, tags, publishedOn):
            return
    
    def getContentPosts(self):
        posts = self.driver.find_elements(By.CLASS_NAME, "c_content_cards__blog_card")
        for content_post in posts:
            meta_container = content_post.find_element(By.CLASS_NAME, "c_content_cards__blog_card__text")

            title = meta_container.find_element(By.CLASS_NAME, "c_content_cards__blog_card__title").text
            tags = meta_container.find_element(By.CLASS_NAME, "c_content_cards__list__category").text
            publishedOn = meta_container.find_elements(By.TAG_NAME, "div")[-1].text
            url = content_post.find_element(By.CLASS_NAME, "c_blog_cards__link").get_attribute('href')
            
            title = self.formatTitle(title)
            url = self.formatURL(url)

            if title is None or url is None:
                return

            authors = self.formatAuthors(None)
            publishedOn = self.formatPublishedOn(publishedOn)
            tags = self.formatTags(tags)

            if not self.handleResource(title, url, authors, tags, publishedOn):
                return

    def getResources(self, page_num=0):
        time.sleep(1)

        if page_num == 0:
            self.getBannerPost()
            self.getContentPosts() 

        container = self.driver.find_element(By.CLASS_NAME, "bg-grey-50")
        container = container.find_element(By.CLASS_NAME, "w-dyn-list").find_element(By.CLASS_NAME, "w-dyn-items")
        posts = container.find_elements(By.XPATH, "div[@role = 'listitem']")
        for post in posts:
            tags, title, date = post.text.split("\n")
            url = post.find_element(By.CLASS_NAME, "c_card_list__link").get_attribute("href")

            title = self.formatTitle(title)
            url = self.formatURL(url)

            if title is None or url is None:
                continue

            authors = self.formatAuthors(None)
            publishedOn = self.formatPublishedOn(date)
            tags = self.formatTags(tags)

            if not self.handleResource(title, url, authors, tags, publishedOn):
                return

        if self.hasNextPage():
            self.getResources(page_num=page_num + 1)


if __name__ == "__main__":
    title = "Deepmind Blog"
    url = "https://www.deepmind.com/blog"
    icon = "https://avatars.githubusercontent.com/u/8596759"
    dateFormat = "%B %d, %Y"

    deepmindblog_client = DeepmindBlogClient(title, url, dateFormat)
    deepmindblog_client.getResources()
    deepmindblog_client.driver.close()