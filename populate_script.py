import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uniwebapp.settings')

import django
django.setup()

from django.contrib.auth.models import User
from petpals.models import UserProfile, Post, Comment, Like
from django.utils import timezone

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
    post.likes.add(user)
    post.save()
    return like

def populate():

    user1 = add_user('alice', 'alice@example.com')
    user2 = add_user('bob', 'bob@example.com')
    user3 = add_user('charlie', 'charlie@example.com')

    post1 = add_post(user1, 'Alices First Post', 'This is Alices first post!', views=100)
    post2 = add_post(user2, 'Bobs Django Adventure', 'Bob talks about learning Django', views=150)
    post3 = add_post(user3, 'Charlies Coding Tips', 'Charlie shares his top coding tips', views=200)

    add_comment(post1, user2, 'Great post Alice!')
    add_comment(post2, user1, 'I love your Django insights, Bob!')
    add_comment(post3, user2, 'Thanks for the tips, Charlie!')

    add_like(user1, post2)
    add_like(user2, post1)
    add_like(user3, post1)

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