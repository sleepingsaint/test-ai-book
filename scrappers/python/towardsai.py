import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class TowardsAIBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h3", {"class": "post-title"})
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h3", {"class": "post-title"})
        a = title_tag.find("a")
        return self.formatURL(a['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOn = tag.find("div", {"class": "post-date"})
        return self.formatPublishedOn(publishedOn.text)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        title_tag = tag.find("h3", {"class": "post-title"})
        a = title_tag.find("a")

        page = requests.get(a['href'])
        soup = BeautifulSoup(page.content, "html.parser")
        container = soup.find("h4", {"class": "medium-author"})

        author_tags = container.find_all("a")
        authors = []
        for author_tag in author_tags:
            authors.append(author_tag.text.strip())

        return self.formatAuthors(authors)

    def getTags(self, tag):
        if tag is None:
            return None

        return self.formatTags(None)

    @tryExceptNone
    def nextPageUrl(self, soup):
        pagination_container = soup.find("ul", {"class": "page-pagination"})
        older_posts = pagination_container.find("a", {"class": "next"})
        if older_posts is not None and older_posts['href'] != "":
            return older_posts['href']
        return None

    def getResources(self):
        page_url = self.url
        while True:
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            container = soup.find("div", {"class": "page-main-content"})
            posts = container.find_all("div", {"class": "post"})

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

            page_url = self.nextPageUrl(soup)
            if page_url is None:
                break

if __name__ == "__main__":
    title = "Towards AI Blog"
    url = "https://towardsai.net/p"
    dateFormat = "%B %d, %Y"

    towardsaiblog_client = TowardsAIBlogClient(title, url, dateFormat)
    towardsaiblog_client.getResources()