import os
<<<<<<< HEAD
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniwebapp.settings')

import django
django.setup()

from petpals.models import Category, Page
from django.utils.text import slugify



def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p

def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.slug = slugify(name)
    c.save()
    return c

def populate():
    python_cat = add_cat('Python', views=128, likes=64)

    add_page(python_cat, "Official Python Tutorial",
             "http://docs.python.org/3/tutorial/", views=50)
    add_page(python_cat, "How to Think like a Computer Scientist",
             "http://www.greenteapress.com/thinkpython/", views=45) 
    add_page(python_cat, "Learn Python",
             "http://www.learnpython.org/", views=40)

    django_cat = add_cat('Django', views=64, likes=32)

    add_page(django_cat, "Official Django Tutorial",
             "https://docs.djangoproject.com/en/2.1/intro/tutorial01/", views=80)
    add_page(django_cat, "Django Rocks",
             "http://www.djangorocks.com/", views=60)
    add_page(django_cat, "How to Tango with Django",
             "http://www.tangowithdjango.com/", views=70)  

    other_cat = add_cat('Other Frameworks', views=32, likes=16)

    add_page(other_cat, "Bottle",
             "http://bottlepy.org/docs/dev/", views=25)  
    add_page(other_cat, "Flask",
             "http://flask.pocoo.org", views=20)
    
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f'- {c}: {p}')

if __name__ == '__main__':
    print('Starting petpals population script...')
    populate()
=======

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniwebapp.settings')

import django

django.setup()

from django.contrib.auth.models import User
from petpals.models import UserProfile, Post, Comment, Like
from django.utils import timezone
import random


def add_user(username, email, password="testpassword"):
    user = User.objects.get_or_create(username=username, email=email)[0]
    user.set_password(password)
    user.save()
    profile = UserProfile.objects.get_or_create(user=user)[0]
    return user, profile


def add_post(user, title, statement, views=0):
    post = Post.objects.get_or_create(user=user, title=title, statement=statement)[0]
    post.views = views
    post.time = timezone.now()
    post.save()
    return post


def add_comment(post, user, content):
    comment = Comment.objects.get_or_create(post=post, user=user, content=content)[0]
    comment.time = timezone.now()
    comment.save()
    return comment


def add_like(user, post):
    like = Like.objects.get_or_create(user=user, post=post)[0]
    return like


def populate():
    # Create Users
    user1, profile1 = add_user('alice', 'alice@example.com')
    user2, profile2 = add_user('bob', 'bob@example.com')
    user3, profile3 = add_user('charlie', 'charlie@example.com')

    # Create Posts
    post1 = add_post(user1, 'Alice’s First Post', 'This is Alice’s first post!', views=100)
    post2 = add_post(user2, 'Bob’s Django Adventure', 'Bob talks about learning Django', views=150)
    post3 = add_post(user3, 'Charlie’s Coding Tips', 'Charlie shares his top coding tips', views=200)

    # Create Comments
    add_comment(post1, user2, 'Great post Alice!')
    add_comment(post2, user1, 'I love your Django insights, Bob!')
    add_comment(post3, user2, 'Thanks for the tips, Charlie!')

    # Add Likes
    add_like(user1, post2)
    add_like(user2, post1)
    add_like(user3, post1)

    # Output to verify
    for user in User.objects.all():
        for post in Post.objects.filter(user=user):
            print(f'{user.username} wrote: {post.title}')
            for comment in Comment.objects.filter(post=post):
                print(f'-- {comment.user.username} commented: {comment.content}')
            for like in post.likes.all():
                print(f'-- Liked by: {like.username}')


if __name__ == '__main__':
    print('Starting petpals population script...')
    populate()
>>>>>>> 7e2e3ddd6d15ca3b920c6ebb50857e14427fe87f
