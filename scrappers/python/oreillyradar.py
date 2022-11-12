import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class OReillyRadarBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h2")
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h2")
        a = title_tag.find("a")
        return self.formatURL(a['href'])
    
    @tryExceptNone
    def getPostDate(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        span = soup.find("span", {"class": "radar-post-page-date"})
        return span.text.strip()

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        title_tag = tag.find("h2")
        a = title_tag.find("a")
        publishedOn = self.getPostDate(a['href'])
        return self.formatPublishedOn(publishedOn)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        meta_container = tag.find("div", {"class": "radar-card-meta"})
        author_tags = meta_container.find_all("a")
        authors = []
        for author_tag in author_tags:
            authors.append(author_tag.text.strip())
        return self.formatAuthors(authors)

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        return self.formatTags(None)

    @tryExceptNone
    def nextPageUrl(self, soup):
        pagination_container = soup.find("div", {"class": "radar-categoryPagination"})
        older_posts = pagination_container.find("span", {"class": "radar-categoryPagination-next"})
        a = older_posts.find("a")
        return a['href']


    def getFeaturedPosts(self):
        
        def getAuthorsAndPublishedOn(url):
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            authors = []
            try:
                authors_container = soup.find("span", {"class": "radar-post-page-author"})
                author_tags = authors_container.find_all("a")
                for tag in author_tags:
                    authors.append(tag.text.strip())
            except:
                pass

            publishedOn = None
            try:
                span = soup.find("span", {"class": "radar-post-page-date"})
                publishedOn = span.text.strip()
            except:
                pass

            return self.formatAuthors(authors), self.formatPublishedOn(publishedOn)

        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        posts = soup.find_all("article", {"class": "featureGrid-card"})
        
        for post in posts:
            title = self.getTitle(post)
            url = post.find("a")['href']
            
            if title is None or url is None:
                continue
            
            authors, publishedOn = getAuthorsAndPublishedOn(url)
            tags = self.getTags(post)
            
            self.handleResource(title, url, authors, tags, publishedOn)
    
    def getResources(self, initial_url):
        page_url = initial_url
        while True:
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            posts = soup.find_all("article", {"class": "radar-card"})

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
    title = "O`Reilly AI & ML Radar Blog"
    url = "https://www.oreilly.com/radar/topics/ai-ml/"
    dateFormat = "%B %d, %Y"

    oreillyradarblog_client = OReillyRadarBlogClient(title, url, dateFormat)
    oreillyradarblog_client.getFeaturedPosts()
    oreillyradarblog_client.getResources(url)