import requests
from bs4 import BeautifulSoup
from utils.python.aibook_client import AIBookClient 
from utils.python.decorators import tryExceptNone

class AnalyticsVidhyaBlogClient(AIBookClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url, dateFormat)

    @tryExceptNone
    def getTitle(self, tag):
        if tag is None:
            return None

        title = tag.find("h4")
        if title is not None:
            return self.formatTitle(title.text)
        return None
    
    @tryExceptNone
    def getURL(self, tag):
        if tag is None:
            return None

        title = tag.find("h4")
        a = title.parent
        return self.formatURL(a['href'])

    @tryExceptNone
    def getAuthors(self, tag):
        if tag is None:
            return None
        
        h6 = tag.find("h6")
        author_tag = h6.find_all("a")[-1]
        return self.formatAuthors(author_tag.text.split(','))
    
    @tryExceptNone
    def getPublishedOn(self, tag):
        if tag is None:
            return None
        
        h6 = tag.find("h6")
        date_str = h6.text.strip()
        a_tags = h6.find_all("a")
        if len(a_tags) > 0:
            author = a_tags[-1].text
            date_str = date_str.replace(author, "")
            date_str = date_str[2:]
        return self.formatPublishedOn(date_str)

    @tryExceptNone
    def getTags(self, tag=None):
        if tag is None:
            return self.formatTags(None)
        tags_span = tag.find("span")
        tags_elements = tags_span.find_all("a")
        tags = []
        for ele in tags_elements:
            tags.append(ele.text.strip())
        return self.formatTags(tags)
    
    def getResources(self):
        page_num = 1

        while True:
            page = requests.get(self.url + f"page/{page_num}/")
            soup = BeautifulSoup(page.content, 'html.parser')
            container = soup.find("section", class_="listing-page")
            
            ul = container.find("ul")
            posts = ul.find_all("li")
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

            if soup.find("a", class_="next") is not None:
                page_num += 1
            else:
                break


if __name__ == "__main__":
    title = "Analytics Vidhya Blog"
    url = "https://www.analyticsvidhya.com/blog-archive/"
    dateFormat = "%B %d, %Y"

    analyticsvidhyablog_client = AnalyticsVidhyaBlogClient(title, url, dateFormat)
    analyticsvidhyablog_client.getResources()