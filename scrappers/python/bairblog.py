import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class BAIRBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
    
        title_tag = tag.find("h1", class_="post-title")
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        url = tag.find("a", class_="post-link")['href']
        return self.formatURL("https://bair.berkeley.edu" + url)

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        meta_tags = tag.find_all("span", class_="post-meta")
        publishedOn = meta_tags[1].text
        return self.formatPublishedOn(publishedOn)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        meta_tags = tag.find_all("span", class_="post-meta")
        authors = meta_tags[0].text
        return self.formatAuthors(authors.split(','))

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None
        return self.formatTags(None)

    @tryExceptNone
    def nextPageUrl(self, soup):
        older = soup.find("div", class_="right")
        a = older.find("a", class_="pagination-item")
        url = "https://bair.berkeley.edu" + a['href']
        return url 

    def getResources(self, page_url):

        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        container = soup.find("div", class_="posts")
        posts = container.findChildren("div", recursive=False) 

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
    title = "BAIR Blog"
    url = "https://bair.berkeley.edu/blog/"
    dateFormat = "%b %d, %Y"

    bairblog_client = BAIRBlogClient(title, url, dateFormat)
    bairblog_client.getResources(url)