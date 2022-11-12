import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone

class AmazonScienceBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        title_tag = tag.find("div", {"class": "PromoF-title"})
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("div", {"class": "PromoF-title"})
        a = title_tag.find("a")
        return self.formatURL(a['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOn = tag.find("div", {"class": "PromoF-date"})
        return self.formatPublishedOn(publishedOn.text)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        authors = tag.find("div", {"class": "PromoF-authors"})
        return self.formatAuthors(authors.text)

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        tags = tag.find("div", {"class": "PromoF-category"})
        return self.formatTags(tags.text)

    @tryExceptNone
    def nextPageUrl(self, soup):
        pagination_container = soup.find("div", {"class": "SearchResultsModule-nextPage"})
        older_posts = pagination_container.find("a")
        if older_posts is not None:
            return older_posts['href']
        return None

    def getResources(self, page_url):
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        posts = soup.find_all("li", {"class": "SearchResultsModule-results-item"})
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
        if nextPageURL is not None:
            self.getResources(nextPageURL)

if __name__ == "__main__":
    title = "Amazon Science Blog"
    url = "https://www.amazon.science/blog"
    dateFormat = "%B %d, %Y"

    amazonscienceblog_client = AmazonScienceBlogClient(title, url, dateFormat)
    amazonscienceblog_client.getResources(url)