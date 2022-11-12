import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class AmazonMLBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        title_tag = tag.find("h2", class_="blog-post-title")
        return self.formatTitle(title_tag.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        title_tag = tag.find("h2", class_="blog-post-title")
        a = title_tag.find("a")
        return self.formatURL(a['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        meta = tag.find("footer", class_="blog-post-meta")
        publishedOn = meta.find("time", {"property": "datePublished"})
        return self.formatPublishedOn(publishedOn.text)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        meta = tag.find("footer", class_="blog-post-meta")
        spans = meta.find_all("span", {"property": "author"})
        authors = []
        for span in spans:
            authors.append(span.text)
        return self.formatAuthors(authors)

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        meta = tag.find("footer", class_="blog-post-meta")
        categories_tag = meta.find("span", {"class": "blog-post-categories"})
        tag_elements = categories_tag.find_all("span", {"property": "articleSection"})
        
        tags = []
        for ele in tag_elements:
            tags.append(ele.text)
        
        return self.formatTags(tags)

    @tryExceptNone
    def nextPageUrl(self, soup):
        pagination_container = soup.find("div", {"class": "blog-pagination"})
        older_posts = pagination_container.find("a")
        if older_posts.text.find("Older posts") != -1:
            return older_posts['href']
        return None

    def getResources(self, page_url):
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        posts = soup.find_all("article", class_="blog-post")

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
    title = "Amazon ML Blog"
    url = "https://aws.amazon.com/blogs/machine-learning/"
    dateFormat = "%d %b %Y"

    amazonmlblog_client = AmazonMLBlogClient(title, url, dateFormat)
    amazonmlblog_client.getResources(url)