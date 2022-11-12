import os
import sys
import sqlite3
from sqlite3 import Error as SQLError

class DBClient:
    def __init__(self, logger) -> None:
        self.logger = logger
        
        db_path = os.environ.get("db_path", "database.db")

        # getting the database connection
        self.conn = self.__getDBConn(db_path)
        if self.conn is None:
            self.logger.error("[DATABASE] Cannot able to connect to database")
            return sys.exit("Unable to connect to database")
        
        # ensuring the tables
        if not self.__ensureTables():
            self.logger.error("[DATABASE] Cannot able to create tables")
            return sys.exit("Unable to create tables")

    def __getDBConn(self, db_path):
        conn = None
        try:
            conn = sqlite3.connect(db_path)
        except SQLError as e:
            self.logger.error(e)
            print(e)
        return conn
    
    def __ensureTables(self):
        sources_table_sql = """
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL
            );
        """

        resources_table_sql = """
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                authors TEXT,
                tags TEXT,
                publishedOn TEXT,
                source_id INTEGER NOT NULL,
                FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE
            );
        """
        
        if not self.__handleDBTransaction(sources_table_sql, ()):
            return False
        
        if not self.__handleDBTransaction(resources_table_sql, ()):
            return False
        
        return True
    
    # handles database transactions like insert, update, delete
    def __handleDBTransaction(self, sql, params=()):
        try:
            c = self.conn.cursor()
            c.execute(sql, params)
            self.conn.commit()
        except SQLError as e:
            print(e)
            return False
        return True
    
    # handle database queries like SELECT
    def __handleDBQuery(self, sql, params):
        try:
            c = self.conn.cursor()
            c.execute(sql, params)
            rows = c.fetchall()
        except SQLError as e:
            print(e)
            return None
        return rows
    
    # source utils functions
    def __checkSource(self, url):
        sql = """SELECT * FROM sources where url = ?"""
        res = self.__handleDBQuery(sql, (url,))
        if res is None or len(res) == 0:
            return False
        return True
    
    def __getSourceId(self, url: str):
        sql = """SELECT * FROM sources where url = ?"""
        res = self.__handleDBQuery(sql, (url,))
        if res is None or len(res) == 0:
            return -1
        return res[0][0]

    def __addSource(self, title: str, url: str) -> int:
        sql = """INSERT INTO sources (title, url) VALUES (?, ?)"""
        if self.__handleDBTransaction(sql, (title, url)):
            self.logger.info(f"[SOURCE]:[ADD] {title}")
            return self.__getSourceId(url)

        self.logger.error(f"[SOURCE]:[ADD] {title}")
        return -1 

    def __deleteSource(self, url):
        if not self.__checkSource(url):
            return True

        sql = """DELETE FROM sources WHERE url = ?"""
        if not self.__handleDBTransaction(sql, (url,)):
            self.logger.error(f"[SOURCE]:[DELETE] {url}")
            return False

        self.logger.info(f"[SOURCE]:[DELETE] {id}")
        return True

    def handleSource(self, title, url, delete=False):
        if delete:
            return self.__deleteSource(url)
        if self.__checkSource(url):
            return self.__getSourceId(url)
        return self.__addSource(title, url)

    # Resource Utils function
    def __checkResource(self, url):
        sql = """SELECT * FROM resources WHERE url = ?"""
        res = self.__handleDBQuery(sql, (url,))
        if res is None or len(res) == 0:
            return False
        return True
    
    def __addResource(self, source_id, title, url, authors, tags, publishedOn):
        sql = """INSERT INTO resources (title, url, authors, tags, publishedOn, source_id) VALUES (?, ?, ?, ?, ?, ?)"""
        if not self.__handleDBTransaction(sql, (title, url, authors, tags, publishedOn, source_id)):
            self.logger.error(f"[RESOURCE]:[ADD] {title}")
            return False

        self.logger.info(f"[RESOURCE]:[ADD] {title}")
        return True

    def __updateResource(self, source_id, title, url, authors=None, tags=None, publishedOn=None):
        if not self.__checkResource(url):
            return False

        if authors is not None:
            sql = """UPDATE resources SET authors = ? WHERE url = ?"""
            if not self.__handleDBTransaction(sql, (authors, url)):
                self.logger.error(f"[RESOURCE]:[UPDATE] {title}")
                return False

        if tags is not None:
            sql = """UPDATE resources SET tags = ? WHERE url = ?"""
            if not self.__handleDBTransaction(sql, (tags, url)):
                self.logger.error(f"[RESOURCE]:[UPDATE] {title}")
                return False

        if publishedOn is not None:
            sql = """UPDATE resources SET publishedOn = ? WHERE url = ?"""
            if not self.__handleDBTransaction(sql, (publishedOn, url)):
                self.logger.error(f"[RESOURCE]:[UPDATE] {title}")
                return False
        
        self.logger.info(f"[RESOURCE]:[UPDATE] {title}")
        return True

    def __deleteResource(self, title, url):
        if not self.__checkResource(url):
            return True
        sql = """DELETE FROM resources WHERE url = ?"""
        if not self.__handleDBTransaction(sql, (url,)):
            self.logger.error(f"[RESOURCE]:[DELETE] {title}")
            return False

        self.logger.info(f"[RESOURCE]:[DELETE] {title}")
        return True

    def handleResource(self, source_id, title, url, authors, tags, publishedOn, delete=False):
        if url is None:
            return False

        if delete:
            return self.__deleteResource(title, url)        
        if not self.__checkResource(url):
            return self.__addResource(source_id, title, url, authors, tags, publishedOn)
        return self.__updateResource(source_id, title, url, authors, tags, publishedOn) 
    

    def getSourceId(self, url):
        return self.__getSourceId(url)

    def sourceExists(self, url):
        return self.__checkSource(url)

    def resourceExists(self, url):
        return self.__checkResource(url)