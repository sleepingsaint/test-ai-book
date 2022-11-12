import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone

class DraganRocksBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        title_tag = tag.find("a")
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("a")
        return self.formatURL(self.url + title_tag['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        span = tag.find("span")
        return self.formatPublishedOn(span.text)

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
        
        posts = soup.find_all("li", {"class": "listing"})
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

if __name__ == "__main__":
    title = "Dragan.rocks Blog"
    url = "https://dragan.rocks"
    dateFormat = "%B %d, %Y"

    draganrocksblog_client = DraganRocksBlogClient(title, url, dateFormat)
    draganrocksblog_client.getResources(url)