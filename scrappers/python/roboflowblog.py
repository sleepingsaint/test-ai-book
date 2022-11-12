import requests
import urllib.parse
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class RoboflowBlog(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str, base_url_prefix: str) -> None:
        super().__init__(title, url, dateFormat)
        self.base_url_prefix = base_url_prefix

    @tryExceptNone    
    def getTitle(self, tag):
        if tag is None or tag.text is None:
            return None 
        return self.formatTitle(tag.text)
    
    @tryExceptNone    
    def getURL(self, tag):
        if tag is None or tag['href'] is None:
            return None
        url = urllib.parse.urljoin(self.base_url_prefix, tag['href'])
        return self.formatURL(url)
    
    @tryExceptNone    
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOnTag = tag.find("div", class_="post-info-block")
        if publishedOnTag is None or publishedOnTag.text is None:
            return None
        return self.formatPublishedOn(publishedOnTag.text)

    @tryExceptNone    
    def getAuthors(self, tag):
        if tag is None:
            return None
        
        info_tags = tag.find_all("div")
        if len(info_tags) < 1:
            return None
        
        authors_div = info_tags[0]
        if authors_div is None:
            return None

        authors = list(map(lambda x: x.text.strip(), authors_div.find_all("a")))
        return self.formatAuthors(authors)

    def getResources(self, initial_url):
        page_url = initial_url
        while True:
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            posts = soup.find_all("div", class_="post")

            for post in posts:
                url_tag = post.find("a", class_="post-heading-link")
                title_tag = post.find("h3", class_="post-v3-heading")
                post_info = post.find("div", class_="post-info")
                
                # extracting data
                title = self.getTitle(title_tag)
                url = self.getURL(url_tag)
                publishedOn = self.getPublishedOn(post_info)
                authors = self.getAuthors(post_info)
                tags = self.formatTags(None)
                if title is None or url is None:
                    continue

                if not self.handleResource(title, url, authors, tags, publishedOn): 
                    return
            
            olderPostsLink = soup.find("a", class_="w-pagination-next")
            if olderPostsLink is None:
                return

            page_url = urllib.parse.urljoin(self.base_url_prefix, olderPostsLink['href'])

if __name__ == "__main__":
    title = "Roboflow Blog"
    url = "https://blog.roboflow.com/latest/"
    base_url_prefix = "https://blog.roboflow.com/"
    dateformat = "%b %d, %Y"

    roboflowblog_client = RoboflowBlog(title, url, dateformat, base_url_prefix)
    roboflowblog_client.getResources(url)