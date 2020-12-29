from datetime import datetime

from flask import url_for
import json

from . import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    @staticmethod
    def insert_categories():
        categories = [
            "Books and Magazines",
            "Entertainment",
            "Electronics",
            "Food and Beverage",
            "Clothing",
            "Health and Beauty"
        ]
        for c in categories:
            existing_category = Category.query.filter_by(name=c).first()
            if not existing_category:
                new_category = Category(name=c)
                db.session.add(new_category)
        db.session.commit()


class Comment(db.Model):
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    created_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    text = db.Column(db.Text, nullable=False)

    def to_json(self):
        return {
            "author": self.author,
            "created_time": self.created_time,
            "text": self.text,
        }

    @staticmethod
    def from_json(json_comment):
        text = json_comment.get("text")
        return Comment(text=text)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200))
    url = db.Column(db.String(200))
    coupon_code = db.Column(db.String(20))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    created_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    category = db.relationship("Category", backref="posts")
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    def to_json(self):
        return {
            "url": url_for("api.get_post", id=self.id),
            "coupon_code": self.coupon_code,
            "product_url": self.url,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "created_time": self.created_time,
            "title": self.title,
            "category": self.category.name,
            "description": self.description,
            "comment_count": self.comments.count(),
            "author": self.author
        }

    @staticmethod
    def from_json(json_post):
        category = Category.query.filter_by(name=json_post.get("category")).first()
        new_post = Post(
            start_date=json_post.get("start_date"),
            end_date=json_post.get("end_date"),
            title=json_post.get("title"),
            category_id=category.id,
            description=json_post.get("description"),
            url=json_post.get("url"),
            coupon_code=json_post.get("coupon_code")
        )
        return new_post