import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient
from utils.python.decorators import tryExceptNone

class DistillPubBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

        # to convert the distill.pub date format to iso format
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None
        title = tag.find("h2", class_="title")
        return self.formatTitle(title.text)
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None
        
        a = tag.findChildren("a", recursive=False)[0]
        return self.formatURL(self.url + a['href'])

    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None

        publishedOn = tag.find("div", class_="publishedDate").text
        month = self.months.index(publishedOn[:3]) + 1
        date_idx = publishedOn.find(" ")
        return self.formatPublishedOn(str(month) + " " + publishedOn[date_idx:])

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None

        authors_tag = tag.find("p", class_="authors")
        return self.formatAuthors(authors_tag.text)

    @tryExceptNone
    def getTags(self, tag):
        if tag is None:
            return None

        tags_container = tag.find("div", class_="tags")
        tag_spans = tags_container.find_all("span")
        tags = []
        for span in tag_spans:
            tags.append(span.text)
        return self.formatTags(tags)
    
    def getResources(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        posts = soup.find_all("div", class_="post-preview")
        
        for post in posts:
            title = self.getTitle(post)
            url = self.getURL(post)

            if title is None or url is None:
                continue
            
            authors = self.getAuthors(post)
            tags = self.getTags(post)
            publishedOn = self.getPublishedOn(post)
           
            if not self.handleResource(title, url, authors, tags, publishedOn):
                return

if __name__ == "__main__":
    title = "Distill Pub Blog"
    url = "https://distill.pub/"
    dateFormat = "%m %d, %Y"

    distillpubblog_client = DistillPubBlogClient(title, url, dateFormat)
    distillpubblog_client.getResources()