# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import datetime
import mysql.connector
import sys


class OlxScraperPipeline(object):
    host = '127.0.0.1'
    user = 'root'
    password = '820'
    db = 'smsword_db'
    def __init__(self):
        self.connection = mysql.connector.connect(self.host, self.user, self.password, self.db)
        self.cursor = self.connection.cursor()


    def process_item(self, item, spider):
        self.cursor.execute(("""SELECT id FROM cities WHERE cities.display_name LIKE '%s'"""), (item["City"].encode('utf-8')))
        result = self.cursor.fetchone()
        if result["id"] is not None:
            city_id = result["id"]

        if item["Area"] is not None:
            self.cursor.execute("SELECT id FROM areas WHERE area.city_id = " + city_id + ", areas.display_name LIKE \"" + item["Area"].encode('utf-8') + "\"")
            result = self.cursor.fetchone()
            if result["id"] is not None:
                area_id = result["id"]
        if item["District"] is not None:
            self.cursor.execute("SELECT id FROM districts WHERE district.display_name LIKE " + item["District"])
            result = self.cursor.fetchone()
            if result["id"] is not None:
                district_id = result["id"]
        now = datetime.datetime.now()
        query = """INSERT INTO mobile_numbers (country_code, city_id"""
        if item["Area"] is not None:
            query += """, area_id"""
        if item["District"] is not None:
            query += """, district_id"""
        query += ", number, create_at, update_at) VALUES(%s, %s, %s, %s, %s"""
        if item["Area"] is not None:
            query += """, %s"""
        if item["District"] is not None:
            query += """, %s"""
        query += ")"
        if item["Area"] is not None:
            data = (
                "UA", city_id, item["Phone_Num"], now.strftime("%Y-%m-%d %H:%M:%S"),
                now.strftime("%Y-%m-%d %H:%M:%S"))
        elif item["District"] is not None:
            data = (
                "UA", city_id, area_id, item["Phone_Num"], now.strftime("%Y-%m-%d %H:%M:%S"),
                now.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            data = (
            "UA", city_id, area_id, district_id, item["Phone_Num"], now.strftime("%Y-%m-%d %H:%M:%S"),
            now.strftime("%Y-%m-%d %H:%M:%S"))
        self.cursor.execute(query, data)
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        return item
