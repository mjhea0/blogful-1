from flask import render_template

from blog import app
from database import session
from models import Post

import mistune
from flask import request, redirect, url_for, g

# imports for login and creating users
from flask import flash
from flask.ext.login import login_user, logout_user
from werkzeug.security import check_password_hash
from models import User

# import for login_required decorator to prevent unauthorzied users
from flask.ext.login import login_required

from flask.ext.login import current_user


@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    # zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    return render_template(
        "posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )


@app.route("/post/add", methods=["GET", "POST"])
#@login_required
def add_post():
    if request.method == "POST":
        post = Post(
            title=request.form["title"],
            content=request.form["content"],
            author=current_user
        )
        session.add(post)
        session.commit()
        return redirect(url_for("posts"))

    return render_template("add_post.html")


@app.route("/post/<int:id>")
def view_post(id):
    post = session.query(Post).get(id)
    return render_template("view_post.html", post=post)


@app.route("/post/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(id):
    if request.method == "POST":
        post = session.query(Post).get(id)
        post.title = request.form["title"]
        post.content = mistune.markdown(request.form["content"])
        session.add(post)
        session.commit()
        return redirect(url_for("posts"))

    post = session.query(Post).get(id)
    return render_template("edit_post.html", post=post)


@app.route("/post/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(id):
    if request.method == "POST":
        post = session.query(Post).get(id)
        if post.author_id == g.user.id:
            session.delete(post)
            session.commit()
            flash("Message deleted!", "success")
        flash("Sorry, you cannot delete that", "danger")
        return redirect(url_for("posts"))

    post = session.query(Post).get(id)
    return render_template("delete_post.html", post=post)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = session.query(User).filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Incorrect username or password", "danger")
            return redirect(url_for("login"))
        login_user(user)
        return redirect(request.args.get('next') or url_for("posts"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out", "danger")
    return redirect(url_for('posts'))


@app.before_request
def before_request():
    g.user = current_user
