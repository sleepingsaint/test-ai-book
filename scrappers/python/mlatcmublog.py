import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class MLAtCMUBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        
        header = tag.find("div", {"class": "post-header"})
        title_tag = header.find("h2")
        if title_tag is None:
            title_tag = header.find("h3")
        
        if title_tag is None:
            return self.formatTitle(None)
        
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        header = tag.find("div", {"class": "post-header"})
        title_tag = header.find("h2")

        if title_tag is None:
            title_tag = header.find("h3")
        
        if title_tag is None:
            return self.formatURL(None)
        
        a = title_tag.find("a")
        return self.formatURL(a['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        meta = tag.find("div", {"class": "post-info"})
        publishedOn = meta.find("span", {"class": "date"})
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

        header = tag.find("div", {"class": "post-header"})
        category = header.find("span", {"class": "category-post"})
        tag_elements = category.find_all("a")
        tags = []
        for ele in tag_elements:
            tags.append(ele.text.capitalize().strip())
        return self.formatTags(tags)

    @tryExceptNone
    def nextPageUrl(self, soup):
        pagination_container = soup.find("div", {"class": "pagination"})
        older_posts = pagination_container.find("div", {"class": "older"})
        a = older_posts.find("a")
        if a is not None:
            return a['href']
        return None

    def getResources(self, initial_url):
        page_url = initial_url
        while True:
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            container = soup.find("div", {"class": "post-list"})
            posts = container.find_all("aside", {"class": "post"})

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
    title = "ML@CMU Blog"
    url = "https://blog.ml.cmu.edu/"
    dateFormat = "%B %d, %Y"

    mlatcmublog_client = MLAtCMUBlogClient(title, url, dateFormat)
    mlatcmublog_client.getResources(url)