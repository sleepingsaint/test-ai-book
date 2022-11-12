import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class HunchNetBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h3", {"class": "entry-title"})
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h3", {"class": "entry-title"})
        a = title_tag.find("a")
        return self.formatURL(a['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOn = tag.find("time", {"class": "entry-date"})
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
    def nextPageUrl(self, soup):
        pagination = soup.find("nav", {"class": "pagination"})
        next_page_url = pagination.find("a", {"class": "next"})
        if next_page_url is not None:
            return next_page_url['href']
        return None

    def getResources(self, initial_url):
        page_url = initial_url
        while True:
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            posts = soup.find_all("article", {"class": "post"})

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

            nextPageURL = self.nextPageUrl(soup)
            if nextPageURL is None:
                break
            page_url = nextPageURL

if __name__ == "__main__":
    title = "Hunch.net Blog"
    url = "https://hunch.net/"
    dateFormat = "%m/%d/%Y"

    hunchnetblog_client = HunchNetBlogClient(title, url, dateFormat)
    hunchnetblog_client.getResources(url)