import sqlite3
connection=sqlite3.Connection('posts_db.db')
with open("schema.sql") as f:
    connection.executescript(f.read())
cursor=connection.cursor()
cursor.execute("insert into posts (title,content) values (?,?)",
               ('my first post','i love programming'))
cursor.execute("insert into posts (title,content) values (?,?)",
               ('my second post','i love problem solving'))

connection.commit()
connection.close()