import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class KoaningIOBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        title_tag = tag.find("b")
        return self.formatTitle(tag.text)

    @tryExceptNone  
    def getURL(self, tag):
        if tag is None:
            return None

        url_tag = tag.find("b").find("a") 
        return self.formatURL(self.url + url_tag['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        date_str = tag.text
        year, month, day = date_str.split("-")
        if len(year) > len(day):
            return self.formatPublishedOn(date_str)
        return self.formatPublishedOn(f"{day}-{year}-{month}")

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        return self.formatAuthors(None)

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None
        return self.formatTags(None)

    def getResources(self, page_url):
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        container = soup.find("article").find("div")
        posts = container.find_all("div")
        
        for idx in range(0, len(posts), 3):
            post = posts[idx + 1]

            title = self.getTitle(post)
            url = self.getURL(post)
            if title is None or url is None:
                continue
            
            post = posts[idx]
            authors = self.getAuthors(post)
            publishedOn = self.getPublishedOn(post)
            tags = self.getTags(post)

            print(publishedOn)
            if not self.handleResource(title, url, authors, tags, publishedOn):
                return

if __name__ == "__main__":
    title = "Koaning.io Blog"
    url = "https://koaning.io/"
    dateFormat = "%Y-%m-%d"

    koaningioblog_client = KoaningIOBlogClient(title, url, dateFormat)
    koaningioblog_client.getResources(url)