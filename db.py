# coding=utf-8
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="cb2"
)
conn = mydb.cursor()