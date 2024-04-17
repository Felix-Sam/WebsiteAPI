from sqlalchemy import create_engine, Column, Integer,DateTime, Text
from fastapi import FastAPI, UploadFile, HTTPException, File
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
import sqlalchemy.orm
import psycopg2
import uuid
import os

load_dotenv()
database_url = os.getenv('DATABASE_URL')
SQLALCHEMY_DATABASE_URL = database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


class PostBlogModel(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    content = Column(Text)
    author = Column(Text)
    date_posted = Column(DateTime, default=datetime.now)


Base.metadata.create_all(bind=engine)


class BlogData(BaseModel):
    content: str
    title: str
    author: str


app = FastAPI()


# Endpoint for uploading and saving images
#@app.post('/upload_image')
#async def upload_image(image: UploadFile = File(...)):
    #filename = f'image_{uuid.uuid4().hex}.jpg'
    #save_path = os.path.join('images', filename)
    #with open(save_path, 'wb') as f:
        #f.write(await image.read())
    #image_url = f'/images/{filename}'
    #return {'image_url': image_url}


# Post a blog
@app.post('/addblogpost')
async def create_blog(blogpost: BlogData):
    db = SessionLocal()
    new_blog = PostBlogModel(
        title=blogpost.title,
        content=blogpost.content,
        author=blogpost.author,
        date_posted=datetime.now(),
    )

    db.add(new_blog)
    db.commit()
    return new_blog


# Get all available blogs
@app.get('/get_all_blogposts')
async def get_all_posts():
    db = SessionLocal()
    all_blogposts = db.query(PostBlogModel).all()
    available_blogs = []

    for blog in all_blogposts:
        blog_data = {
            'id': blog.id,
            'title': blog.title,
            'content': blog.content,
            'date_posted': blog.date_posted,
            'author': blog.author,
        }
        available_blogs.append(blog_data)

    return available_blogs


# Delete a Blog
@app.delete('/delete_blog')
async def delete_blog(id: int):
    db = SessionLocal()
    blog_to_delete = db.query(PostBlogModel).filter_by(id=id).first()

    if blog_to_delete:
        db.delete(blog_to_delete)
        db.commit()
        return f'Blog with ID {id} deleted successfully'
    else:
        return f'Blog with ID {id} does not exist'


# Update blog status
@app.put('/blogs/{blog_id}')
async def update_blog(blog_id: int, blogs: BlogData):
    db = SessionLocal()
    post = {
        "title": blogs.title,
        "content": blogs.content,
        "author": blogs.author,
        "date_posted": datetime.now(),
    }

    existing_blog = db.query(PostBlogModel).filter(PostBlogModel.id == blog_id).first()
    if not existing_blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    for key, value in post.items():
        setattr(existing_blog, key, value)

    db.commit()
    return post