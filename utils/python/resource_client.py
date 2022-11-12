import os
from utils.python.db_client import DBClient
import logging

class ResourceClient:
    def __init__(self, title: str, url: str) -> None:
        
        logging_format=f"[%(levelname)s]:[%(asctime)s]:[{title}] %(message)s"
        logging.basicConfig(filename="resource_scrapper.log", format=logging_format)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.db = DBClient(self.logger)

        # flag to refetch the entire posts or just check for new posts
        # if source is not added yet or manually enter
        self.refetch = int(os.environ.get("REFETCH", 0)) == 1
        self.refetch = self.refetch or not self.db.sourceExists(url)

        self.db.handleSource(title, url)
        self.source_id = self.db.getSourceId(url)

    def getResources(self, *args, **kwargs):
        pass