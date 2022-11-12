import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class GoogleAIClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)
    
    @tryExceptNone
    def getTitle(self, post):
        title = post.find("h3", class_="post-title")
        return self.formatTitle(title.text)
    
    @tryExceptNone
    def getURL(self, post):
        return self.formatURL(post['href'])
    
    @tryExceptNone
    def getPublishedOn(self, post):
        tag = post.find("time")
        return tag['datetime']

    def getAuthors(self, post):
        return None

    def getTags(self, post):
        return None

    def getHeroPost(self, soup):
        hero = soup.find("div", class_="heroPost")

        title_tag = hero.find("h3", class_="post-title")

        title = self.formatTitle(title_tag.text)
        url = self.formatURL(title_tag.find("a")['href'])
        publishedOn = self.getPublishedOn(hero)
        authors = self.getAuthors(hero)
        tags = self.getTags(hero)

        if not self.handleResource(title, url, authors, tags, publishedOn):
            return

    def getResources(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        posts = soup.find_all("a", class_="post-outer-container")

        if url == "https://ai.googleblog.com/":
            self.getHeroPost(soup)

        for post in posts:
            title = self.getTitle(post)
            url = self.getURL(post)
            
            authors = self.getAuthors(post)
            tags = self.getTags(post)
            publishedOn = self.getPublishedOn(post)
            
            if not self.handleResource(title, url, authors, tags, publishedOn):
                return

        olderPostsLink = soup.find("a", id="olderPostsBtn", href=True)

        if(olderPostsLink != None):
            self.getResources(olderPostsLink['href'])

if __name__ == "__main__":
    title = "Google AI Blog"
    url = "https://ai.googleblog.com/"
    dateFormat = "%A, %B %d, %Y"

    googleaiblog_client = GoogleAIClient(title, url, dateFormat)
    googleaiblog_client.getResources(url)
