#! /usr/bin/python3

import sqlite3

class DBMan:
#Crawler 테이블 최초 작성

	def __init__(self, dbname = r"/PATH/TO/DATABASE/kic.db"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname, check_same_thread = False)

	def setup(self):
		stmt = "CREATE TABLE IF NOT EXISTS Und_Pinned (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt)
		stmt1 = "CREATE TABLE IF NOT EXISTS Und_Normal (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt1)
		stmt2 = "CREATE TABLE IF NOT EXISTS JnA_Pinned (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt2)
		stmt3 = "CREATE TABLE IF NOT EXISTS JnA_Normal (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt3)
		stmt4 = "CREATE TABLE IF NOT EXISTS Sch_Pinned (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt4)
		stmt5 = "CREATE TABLE IF NOT EXISTS Sch_Normal (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt5)
		stmt6 = "CREATE TABLE IF NOT EXISTS Oth_Pinned (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt6)
		stmt7 = "CREATE TABLE IF NOT EXISTS Oth_Normal (notice_date text, crawl_dt text, notice_title text, url text PRIMARY KEY DESC, msg_id int)"
		self.conn.execute(stmt7)
		self.conn.commit()

#Crawler 테이블용 함수 정의

	def add_notice(self, category, notice_date, crawl_dt, notice_title, url, msg_id):
		stmt = f"INSERT OR IGNORE INTO {category} VALUES (?, ?, ?, ?, ?)"
		args = (notice_date, crawl_dt, notice_title, url, msg_id, )
		self.conn.execute(stmt, args)
		self.conn.commit()

	def del_notice(self, category, url):
		stmt = f"DELETE FROM {category} WHERE url = (?)"
		args = (url, )
		self.conn.execute(stmt, args)
		self.conn.commit()

	def get_notices(self, category):
		stmt = f"SELECT url FROM {category}"
		return [x[0] for x in self.conn.execute(stmt)]

	def get_msg_id(self, category, url):
		stmt = f"SELECT msg_id FROM {category} WHERE url = (?)"
		args = (url, )
		return [x[0] for x in self.conn.execute(stmt, args)][0]
