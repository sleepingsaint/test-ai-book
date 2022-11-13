import os
import json
import logging
from utils.python.db_client import DBClient

class Builder(DBClient):
    def __init__(self) -> None:
        logger = logging.getLogger()
        super().__init__(logger)
        self.sources_dir = os.environ.get("sources_dir", "sources/")
        self.resources_dir = os.environ.get("resources_dir", "resources/")

        self.source_page_size = os.environ.get("sources_page_size", 30)
        self.resource_page_size = os.environ.get("resources_page_size", 30)

    def ensureDir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def getAllSources(self):
        sql = """SELECT * FROM sources"""
        return self._DBClient__handleDBQuery(sql, ())

    def getNumResources(self, source_id):
        sql = """SELECT COUNT(*) FROM resources where source_id = ?"""
        return self._DBClient__handleDBQuery(sql, (source_id,))[0][0]

    def getAllResources(self, source_id):
        sql = """SELECT * FROM resources where source_id = ?"""
        return self._DBClient__handleDBQuery(sql, (source_id,))

    def buildSources(self):
        self.ensureDir(self.sources_dir)
        sources = self.getAllSources()
        total = len(sources)
        idx = 0

        if total == 0:
            data = {
                "hasNextPage": False,
                "data": []
            }
            path = os.path.join(self.sources_dir, "0.json")
            with open(path, "w+") as f:
                json.dump(data)
            
            return

        while True:
            start = idx * self.source_page_size
            end = start + self.source_page_size
            hasNextPage = (end < total)
            end = min(end, total)

            data = {}
            data["hasNextPage"] = hasNextPage
            data["data"] = []
            for i in range(start, end):
                
                source = {}
                source["id"] = sources[i][0]
                source['title'] = sources[i][1]
                source['url'] = sources[i][2]
                source["numResources"] = self.getNumResources(sources[i][0])

                data["data"].append(source)

            path = os.path.join(self.sources_dir, f"{idx}.json") 
            with open(path, "w+") as f:
                json.dump(data, f, indent=4)

            idx += 1
            if not hasNextPage:
                break

    def buildResources(self):
        self.ensureDir(self.resources_dir)
        sources = self.getAllSources()

        for source in sources:
            source_id = source[0]
            total = self.getNumResources(source_id)
            resources = self.getAllResources(source_id)
            idx = 0
            
            self.ensureDir(os.path.join(self.resources_dir, str(source_id)))

            if total == 0:
                path = os.path.join(self.resources_dir, str(source_id), "0.json")
                data = {
                    "hasNextPage": False,
                    "data": []
                }
                with open(path, "w+") as f:
                    json.dump(data)
                
                continue

            while True:
                start = idx * self.source_page_size
                end = start + self.source_page_size
                hasNextPage = (end < total)
                end = min(end, total)

                data = {}
                data["hasNextPage"] = hasNextPage
                data["data"] = []
                for i in range(start, end):
                    
                    resource = {}
                    resource["id"] = resources[i][0]
                    resource['title'] = resources[i][1]
                    resource['url'] = resources[i][2]
                    resource['authors'] = resources[i][3]
                    resource['tags'] = resources[i][4]
                    resource['publishedOn'] = resources[i][5]

                    data["data"].append(resource)

                path = os.path.join(self.resources_dir, str(source_id), f"{idx}.json") 
                with open(path, "w+") as f:
                    json.dump(data, f, indent=4)

                idx += 1
                if not hasNextPage:
                    break

    def build(self):
        self.buildSources()
        self.buildResources()
            
builder = Builder()
builder.build()