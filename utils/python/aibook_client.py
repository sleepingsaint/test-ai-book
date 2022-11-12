from datetime import datetime
from typing import List, Union
from utils.python.resource_client import ResourceClient

class AIBookClient(ResourceClient):
    def __init__(self, title: str, url: str, dateFormat: str) -> None:
        super().__init__(title, url)
        self.url = url
        self.dateFormat = dateFormat

    def formatTitle(self, title: str) -> str:
        return title.strip()

    def formatURL(self, url: str) -> str:
        return url.strip()

    def formatPublishedOn(self, date: str) -> str:
        if date is None or self.dateFormat is None:
            return date

        date = date.strip()
        publishedOn = date
        try:
            _datetime = datetime.strptime(date, self.dateFormat)
            publishedOn = _datetime.isoformat()
        except:
            print("Invalid date format")

        return publishedOn

    def formatAuthors(self, authors: Union[str, List[str], None]):
        if authors is None:
            return authors
        
        if type(authors) is str:
            return authors.strip()
        return ", ".join(list(map(lambda x: x.strip(), authors)))
        
    def formatTags(self, tags: Union[str, List[str], None] = None) -> str:
        if tags is None:
            return tags 
        
        if type(tags) is str:
            tags = tags.strip().split(',')
        return ", ".join(list(map(lambda x: x.strip(), tags)))

    def handleResource(self, title, url, authors, tags, publishedOn):
        if not self.db.resourceExists(url): 
            result = self.db.handleResource(self.source_id, title, url, authors, tags, publishedOn)
            if not result:
                print(f"Resource cannot be created : {title}")
                return False
            return True
        
        elif self.refetch:
            if not self.db.handleResource(self.source_id, title, url, authors, tags, publishedOn):
                print(f"Resource cannot be updated : {title}")
            return True

        return False