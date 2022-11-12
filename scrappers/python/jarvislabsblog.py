import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class JarvisLabsAIBlogClient(AIBookClient):
    def __init__(self, title: str, url: str,  dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
    
        title_tag = tag.find("h2", {"itemprop": "headline"})
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h2", {"itemprop": "headline"})
        a = title_tag.find("a")
        return self.formatURL("https://jarvislabs.ai" + a['href'])
    
    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOn = tag.find("time", {"itemprop": "datePublished"})
        return self.formatPublishedOn(publishedOn.text)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        author_tag = tag.find("div", {"class": "avatar__name"})
        return self.formatAuthors(author_tag.text.split(","))

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        tags_container = tag.find("footer").find("ul")
        tag_elements = tags_container.find_all("a")
        tags = []
        for ele in tag_elements:
            tags.append(ele.text.strip())
            
        return self.formatTags(tags)

    def getResources(self, page_url):
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        posts = soup.find_all("article", {"itemprop": "blogPost"})

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
    title = "Jarvis Labs AI Blog"
    url = "https://jarvislabs.ai/blogs/"
    dateFormat = "%B %d, %Y"

    jarvislabsaiblog_client = JarvisLabsAIBlogClient(title, url, dateFormat)
    jarvislabsaiblog_client.getResources(url)