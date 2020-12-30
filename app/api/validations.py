from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from wtforms.validators import DataRequired


create_post_schema = {
    "type": "object",
    "properties": {
        "start_date": { "type": "string", "format": "date", "minLength": 1 },
        "end_date": { "type": "string", "format": "date", "minLength": 1 },
        "title": { "type": "string", "minLength": 1 },
        "category": { 
            "type": "string", 
            "enum": ["Books and Magazines", "Entertainment", "Electronics", "Food and Beverage", "Clothing", "Health and Beauty"] 
        },
        "description": { "type": "string" },
        "url": { "$ref": "#/definitions/valid_url" },
        "coupon_code": { "type": "string" } 
    },
    "definitions": {
        "valid_url": { "format": "uri", "pattern": "^https?://" }
    },
    "required": ["start_date", "end_date", "title", "category"]
}


class CreatePostInput(Inputs):
    json = [JsonSchema(schema=create_post_schema)]


create_comment_schema = {
    "type": "object",
    "properties": {
        "text": { "type": "string", "minLength": 1 }
    },
    "required": ["text"]
}


class CreateCommentInput(Inputs):
    json = [JsonSchema(schema=create_comment_schema)]


search_posts_schema = {
    "type": "object",
    "properties": {
        "category": { 
            "type": "string",  
            "enum": ["All", "Books and Magazines", "Entertainment", "Electronics", "Food and Beverage", "Clothing", "Health and Beauty"]
        },
        "key": { "type": "string", "minLength": 1 }
    },
    "required": ["key", "category"]
}


class SearchPostInput(Inputs):
    json = [JsonSchema(schema=search_posts_schema)]