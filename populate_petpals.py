import os
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
