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
        "coupon_code": { "type": "string" },
        "image_url": { "$ref": "#/definitions/valid_url" }
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


update_post_vote_schema = {
    "type": "object",
    "properties": {
        "vote_action": { 
            "type": "string",  
            "enum": ["increment", "decrement"]
        }
    },
    "required": ["vote_action"]  
}


class UpdatePostVoteInput(Inputs):
    json = [JsonSchema(schema=update_post_vote_schema)]


report_schema = {
    "type": "object",
    "properties": {
        "reason": {
            "type": "string",
            "enum": [
                "Illegal/Inapproriate",             
                "Spam",
                "Personal Attack",
                "Private Selling",
                "Off-topic",
                "Duplicate"
                "Other"
            ]
        },
        "post_id": {
            "type": "integer"
        },
        "comment_id": {
            "type": "integer"
        },
        "description": {
            "type": "string"
        }
    },
    "anyOf": [
        { "required": ["reason", "post_id"] },
        { "required": ["reason", "comment_id"] }
    ]
}


class ReportInput(Inputs):
    json = [JsonSchema(schema=report_schema)]