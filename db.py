# coding=utf-8
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="chatbot"
)
conn = mydb.cursor()
