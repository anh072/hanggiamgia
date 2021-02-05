# hanggiamgia

A website for Vietnamese people to buy discounted products and bargains

## Local development
Create a virtual environment
```
python3 -m venv hanggiamgia
```

Activate your virtual environment
```
source .venv/bin/activate
```

Install dependencies
```
pip install requirements.txt
```

Bring up the app stack
```
docker-compose up
```

To print out the SQL query, you can do this
```
q = Post.query.join(Comment, Post.id == Comment.post_id).filter(Comment.author == username)
print(str(q))
```

## Database migration
```
python manage.py db init
python manage.py db migrate -m "<message>" # this will generate a migration file
python manage.py db upgrade # perform the migration
```

## User stories
* As a visitor, I can see all the posts and can select categories
* As a vistor, I can sign up for the site either via basic auth or facebook/google
* As an authenticated user, I can create/edit/delete my posts
* As an authenticated user, I can add comments to someone else's posts
* As a visitor, I can see a signed-up user's posts when clicking on his username
* As a visitor, I can search for posts
* As a visitor, I can filter posts by cities

## API
* GET /api/v1/posts?page=<number> : retrieve a paginated list of posts ordered by created time
* GET /api/v1/posts?category=<string>&page=<number> : retrieve a paginated list of posts by a category ordered by created time
* GET /api/v1/posts/<id> : retrieve a post by id
* POST /api/v1/posts : create a post
* PUT /api/v1/posts/<id> : update a post
* GET /api/v1/posts/<id>/comments?page=<number> : retrieve a paginated list of comments of a post
* POST /api/v1/posts/<id>/comments : create a comment for a post
* PUT /api/v1/posts/<id>/comments/<id> : update a comment
* GET /api/v1/users/<username> : retrieve user information
* GET /api/v1/users/<username>/posts?page=<number> : retrieve a paginated list of posts of a user

