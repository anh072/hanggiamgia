from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from wtforms.validators import DataRequired


create_post_schema = {
    "type": "object",
    "properties": {
        "start_date": { "type": "string", "format": "date" },
        "end_date": { "type": "string", "format": "date" },
        "title": { "type": "string" },
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


create_comment_input = {
    "type": "object",
    "properties": {
        "text": { "type": "string" }
    },
    "required": ["text"]
}


class CreateCommentInput(Inputs):
    json = [JsonSchema(schema=create_comment_input)]