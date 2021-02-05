from datetime import datetime
import enum

from flask import url_for
import json
import pytz
from pytz import timezone

from . import db


# get timezones
utc = pytz.utc
local_zone = timezone("Asia/Ho_Chi_Minh")


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
            "id": self.id,
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
    url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    coupon_code = db.Column(db.String(20))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    created_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    votes = db.Column(db.Integer, default=0)
    category = db.relationship("Category", backref="posts")
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    def to_json(self):
        return {
            "id": self.id,
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
            "author": self.author,
            "image_url": self.image_url,
            "votes": self.votes
        }

    def update_from_json(self, json_put):
        self.title = json_put.get("title")

        category = Category.query.filter_by(name=json_put.get("category")).first()
        self.category_id = category.id
        self.description = json_put.get("description")

        # convert to datetime objects
        start_date = datetime.strptime(json_put.get("start_date"), '%Y-%m-%d')
        end_date = datetime.strptime(json_put.get("end_date"), '%Y-%m-%d')
        # datetime object in local timezone
        loc_start_date = local_zone.localize(start_date)
        loc_end_date = local_zone.localize(end_date)
        # datetime object in utc timezone
        utc_start_date = loc_start_date.astimezone(utc)
        utc_end_date = loc_end_date.astimezone(utc)
        self.start_date = utc_start_date.strftime('%Y-%m-%d'),
        self.end_date = utc_end_date.strftime('%Y-%m-%d'),
        self.coupon_code = json_put.get("coupon", None)
        self.url = json_put.get("url", None)
        if json_put.get("image_url"):
            self.image_url = json_put.get("image_url")

    @staticmethod
    def from_json(json_post):
        category = Category.query.filter_by(name=json_post.get("category")).first()

        # convert to datetime objects
        start_date = datetime.strptime(json_post.get("start_date"), '%Y-%m-%d')
        end_date = datetime.strptime(json_post.get("end_date"), '%Y-%m-%d')
        # datetime object in local timezone
        loc_start_date = local_zone.localize(start_date)
        loc_end_date = local_zone.localize(end_date)
        # datetime object in utc timezone
        utc_start_date = loc_start_date.astimezone(utc)
        utc_end_date = loc_end_date.astimezone(utc)
        new_post = Post(
            start_date=utc_start_date.strftime('%Y-%m-%d'),
            end_date=utc_end_date.strftime('%Y-%m-%d'),
            title=json_post.get("title"),
            category_id=category.id,
            description=json_post.get("description"),
            url=json_post.get("url"),
            coupon_code=json_post.get("coupon"),
            image_url=json_post.get("image_url")
        )
        return new_post


class VoteTypeEnum(enum.Enum):
    INCREMENT = "increment"
    DECREMENT = "decrement"


class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), index=True)
    voter = db.Column(db.String(100), nullable=False)
    vote_type = db.Column(db.Enum(VoteTypeEnum))
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "voter": self.voter,
            "vote_type": self.vote_type.value,
            "created_time": self.created_time
        }


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(100), index=True, nullable=False)

class Reason(db.Model):
    __tablename__ = "reasons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    @staticmethod
    def insert_reasons():
        reasons = [
            "Illegal/Inapproriate",
            "Spam",
            "Personal Attack",
            "Private Selling",
            "Off-topic",
            "Duplicate",
            "Other"
        ]
        for c in reasons:
            existing_reason = Reason.query.filter_by(name=c).first()
            if not existing_reason:
                new_reason = Reason(name=c)
                db.session.add(new_reason)
        db.session.commit()


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True) 
    reason_id = db.Column(db.Integer, db.ForeignKey("reasons.id"))   
    post_id = db.Column(db.Integer, nullable=True)
    comment_id = db.Column(db.Integer, nullable=True)
    reporter = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reason = db.relationship("Reason", backref="reports")

    @staticmethod
    def from_json(json_report):
        reason = Reason.query.filter_by(name=json_report.get("reason")).first()
        new_report = Report(
            reason_id=reason.id,
            post_id=json_report.get("post_id"),
            comment_id=json_report.get("comment_id"),
            description=json_report.get("description")
        )
        return new_report
    
    def to_json(self):
        return {
            "id": self.id,
            "reason": self.reason.name,
            "description": self.description,
            "comment_id": self.comment_id,
            "post_id": self.post_id
        }