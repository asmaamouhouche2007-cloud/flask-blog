import sqlite3
from werkzeug.exceptions import abort
from flask import Flask,request,render_template,url_for,flash,redirect
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
from flask import Flask,render_template
app=Flask(__name__)
app.config['SECRET_KEY']='1234'
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
        else:
            conn=get_db_conn('posts_db.db')
            conn.execute('insert into posts (title,content) values (?,?)',(title,content))
            conn.commit()
            conn.close()
        return redirect(url_for('index'))
    return render_template('create.html')
@app.route('/<int:id>/edit',methods=('GET','POST'))
def edit(id):
    post=get_post(id)
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        if not title:
            flash('title is resquired')
        else :
            conn=get_db_conn('posts_db.db')
            conn.execute("UPDATE posts SET title = ? ,content = ? WHERE id = ?",(title,content,id))
            conn.commit()
            conn.close()
        return redirect(url_for('index'))
        
    return render_template('edit.html',post=post)
@app.route('/<int:id>/delete',methods=('POST',))
def delete(id):
    post=get_post(id)
    conn=get_db_conn('posts_db.db')
    conn.execute("delete from posts where id=?",(id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

if __name__ =='__main__':
    app.run(port=5001)