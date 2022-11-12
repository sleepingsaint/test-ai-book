import requests
from bs4 import BeautifulSoup

from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone

class OpenAIClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone        
    def getTitle(self, tag):
        if tag is None:
            return None

        a = tag.find("h5").find("a")
        return self.formatTitle(a.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None

        a = tag.find("h5").find("a")
        return self.formatURL("https://openai.com" + a["href"])
    
    def getAuthors(self, tag):
        return self.formatAuthors(None) 

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None
        
        time = tag.find("time")
        return self.formatPublishedOn(time.text)

    @tryExceptNone
    def getTags(self, tag=None):
        if tag is None:
            return self.formatTags(None)
        ul = tag.find("ul")
        tag_elements = ul.findAll("a")
        tags = []
        for ele in tag_elements:
            tags.append(ele.text.strip())
        return self.formatTags(tags)

    def getResources(self, initial_url):
        url = initial_url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        posts = soup.find_all("div", class_="post-card-full")

        for post in posts:
            title = self.getTitle(post)
            url = self.getURL(post)
            if title is None or url is None:
                continue

            publishedOn = self.getPublishedOn(post)
            authors = self.getAuthors(post)
            tags = self.getTags(post)
            
            if not self.handleResource(title, url, authors, tags, publishedOn):
                return

if __name__ == "__main__":
    title = "OpenAI Blog"
    url = "https://openai.com/blog/"
    dateFormat = "%B %d, %Y"

    openai_client = OpenAIClient(title, url, dateFormat)
    openai_client.getResources(url)