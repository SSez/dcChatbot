# coding=utf-8
import db

def createTag():
    context_tag = 0
    end = 0
    sql = "INSERT INTO tags (context_tag, end) VALUES(%s, %s)"
    val = ( str(context_tag), str(end), )
    db.conn.execute(sql, val)
    db.mydb.commit()
    return db.conn.lastrowid

def check_user(id):
    sql = "SELECT COUNT(*) FROM discord WHERE user_id = %s"
    values = ( str(id), )
    db.conn.execute(sql, values)
    countSQL = db.conn.fetchone()[0]
    return countSQL

def register(**user):
    sql = "INSERT INTO discord (nickname, user_id) VALUES(%s, %s)"
    val = ( str(user['name']), str(user['id']), )
    db.conn.execute(sql, val)
    db.mydb.commit()

def createPattern(output, tag_id):
    sql = "INSERT INTO patterns (tag_id, pattern) VALUES(%s, %s)"
    val = ( str(tag_id), str(output), )
    db.conn.execute(sql, val)
    db.mydb.commit()

def createResponse(output, tag_id):
    sql = "INSERT INTO responses (tag_id, response) VALUES(%s, %s)"
    val = ( str(tag_id), str(output), )
    db.conn.execute(sql, val)
    db.mydb.commit()

def getResponseID(bot_msg):
    sql = "SELECT tag_id FROM responses WHERE response = %s"
    adr = ( str(bot_msg), )
    db.conn.execute(sql, adr)
    SQL_id = db.conn.fetchone()[0]
    return SQL_id

def getResCount(bot_msg, user_msg):
    SQL_id = getResponseID(bot_msg)
    sql = "SELECT COUNT(*) FROM patterns WHERE pattern = %s AND tag_id = %s"
    adr = (str(user_msg), int(SQL_id), )
    db.conn.execute(sql, adr)
    countSQL = db.conn.fetchone()[0]
    return countSQL
    
def insert(question, tag_id):
    sql_insert = "INSERT INTO patterns (tag_id, pattern) VALUES(%s, %s)"
    val_insert = ( int(tag_id), str(question), )
    db.conn.execute(sql_insert, val_insert)
    db.mydb.commit()

def getStatus(user_id):
    sql = "SELECT status FROM discord WHERE user_id = %s"
    values = ( str(user_id), )
    db.conn.execute(sql, values)
    status = db.conn.fetchone()[0]
    return status

def check_pattern(output):
    sql = "SELECT COUNT(*) FROM patterns WHERE pattern = %s"
    adr = (str(output), )
    db.conn.execute(sql, adr)
    countSQL = db.conn.fetchone()[0]
    return countSQL

def check_response(output):
    sql = "SELECT COUNT(*) FROM responses WHERE response = %s"
    adr = (str(output), )
    db.conn.execute(sql, adr)
    countSQL = db.conn.fetchone()[0]
    return countSQL

def get_patterns(tag_id):
    sql = "SELECT * FROM patterns WHERE tag_id = %s"
    adr = (int(tag_id),)
    db.conn.execute(sql, adr)
    row = [x[2] for x in db.conn]
    return row

def get_resonses(tag_id):
    sql = "SELECT * FROM responses WHERE tag_id = %s"
    adr = (int(tag_id),)
    db.conn.execute(sql, adr)
    row = [x[2] for x in db.conn]
    return row

def get_data():
    sql = "SELECT * FROM tags ORDER BY id ASC"
    db.conn.execute(sql)
    rows = db.conn.fetchall()
    data = []
    for x in rows:
        tag = int(x[0])
        context_set = x[1]
        end = x[2]
        patterns = get_patterns(tag)
        responses = get_resonses(tag)
        if patterns and responses:
            data.append({
                "tag": tag,
                "patterns": patterns,
                "responses": responses,
                "context_tag": context_set,
                "end": bool(end)
            })
    return data
