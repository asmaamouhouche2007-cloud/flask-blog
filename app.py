import sqlite3
from werkzeug.exceptions import abort
from flask import Flask,request,render_template,url_for,flash,redirect,g
import os
from dotenv import load_dotenv
import logging,uuid,time
from logging.handlers import RotatingFileHandler
load_dotenv()

app=Flask(__name__)
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')


handler=RotatingFileHandler('app.log',maxBytes=1_000_000,backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.before_request
def before():
    g.request_id=str(uuid.uuid4())[:8]
    g.start_time=time.time()
    app.logger.info(f"[{g.request_id}]--->{request.method} {request.path}")

@app.after_request
def after(response):
    ms=(time.time()-g.start_time)*1000
    app.logger.info(
        f"[{g.request_id}]<---{response.status_code}  "
        f"{request.method} {request.path} ({ms:.1f}ms)"
    )
    return response

@app.errorhandler
def on_error(e):
    app.logger.exception(f"[{g.request_id}] {e}")
    return {"error":"internal error"},500

def get_db_conn(dbname):
    conn=sqlite3.connect(dbname)
    conn.row_factory=sqlite3.Row
    return conn
def get_post(post_id):
    conn=get_db_conn("posts_db.db")
    post=conn.execute("select * from posts where id=?",(post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/')
def index():
    conn=get_db_conn('posts_db.db')
    posts=conn.execute("select * from posts").fetchall()
    conn.close()
    return render_template('index.html',posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post=get_post(post_id)
    return render_template('post.html',post=post)
@app.route('/create',methods=('GET','POST'))
def create():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        if not title:
            flash('title is required !')
            app.logger.info("title was missing from post")
        else:
            conn=get_db_conn('posts_db.db')
            conn.execute('insert into posts (title,content) values (?,?)',(title,content))
            conn.commit()
            conn.close()
            app.logger.info(f"[{g.request_id}] new post entitled :{title} created successfully ")
        return redirect(url_for('index'))
    return render_template('create.html')
@app.route('/<int:id>/edit',methods=('GET','POST'))
def edit(id):
    post=get_post(id)
    previous_title=post["title"]
    previous_content=post["content"]
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        if not title:
            flash('title is resquired')
            app.logger.info(f"[{g.request_id}] title missing from post after editing")
        else :
            conn=get_db_conn('posts_db.db')
            conn.execute("UPDATE posts SET title = ? ,content = ? WHERE id = ?",(title,content,id))
            conn.commit()
            conn.close()
            log_msg=f"[{g.request_id}] post with id {id} edited "
            if title!=previous_title:
                log_msg=log_msg + f"previous title:{previous_title}, new title :{title}"
            if content!=previous_content:
                log_msg=log_msg+ f" content modified either"
            app.logger.info(log_msg)
        return redirect(url_for('index'))
        
    return render_template('edit.html',post=post)
@app.route('/<int:id>/delete',methods=('POST',))
def delete(id):
    post=get_post(id)
    conn=get_db_conn('posts_db.db')
    conn.execute("delete from posts where id=?",(id,))
    conn.commit()
    conn.close()
    app.logger.info(f"[{g.request_id}] post with id {id} deleted ")
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

if __name__ =='__main__':
    app.run(port=5001)