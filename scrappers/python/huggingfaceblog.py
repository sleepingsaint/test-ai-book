import re
import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone

class HuggingFaceBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

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
        return self.formatURL("https://huggingface.co" + tag['href'])

    def convertDateStr(self, date_str):
        items = date_str.split(" ")
        if len(items) < 3:
            if (items[0][0].isalpha()):
                month, year = items
                month = self.months.index(month[:3]) + 1
                day = 1
            elif (items[0][0].isnumeric()):
                day, year = items
                day = re.sub("\D", "", day)
                month = 1
                year = year
        else:
            month, day, year = items
            month = self.months.index(month[:3]) + 1
            day = re.sub("\D", "", day)
            year = year
        
        return f"{day} {month} {year}"

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        meta = tag.find("p")
        spans = meta.find_all("span")
        if len(spans) > 1:
            publishedOn = spans[1]
        else:
            return None
        date_str = self.convertDateStr(publishedOn.text)
        return self.formatPublishedOn(date_str)

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        meta = tag.find("p")
        author = meta.find("a")
        return self.formatAuthors(author.text.split(","))

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        return self.formatTags(None)

    @tryExceptNone
    def nextPageUrl(self, soup):
        pagination_container = soup.find("nav", {"role": "navigation"})
        ul = pagination_container.find("ul")
        li = ul.findChildren("li")[-1]
        a = li.find("a")
        if a['href'] != "":
            return "https://huggingface.co" + a['href']
        return None

    def getResources(self, initial_url):
        page_url = initial_url
        while True:
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            container = soup.find("main").find("div").find("div").findChildren("div", recursive=False)[-1]
            posts = container.findChildren("a", recursive=False)

            if page_url != self.url and len(posts) > 0:
                posts = posts[1:]

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
    title = "Huggingface Blog"
    url = "https://huggingface.co/blog"
    dateFormat = "%d %m %Y"

    huggingfaceblog_client = HuggingFaceBlogClient(title, url, dateFormat)
    huggingfaceblog_client.getResources(url)