from django.shortcuts import render, get_object_or_404, redirect
from petweb.models import Category, Page
from petweb.forms import PageForm, CategoryForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from petweb.models import Post, Comment, UserProfile
from petweb.forms import PostForm, CommentForm
from petweb.forms import UserForm, UserProfileForm
from django.contrib.auth.models import User 




def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    visitor_cookie_handler(request)
    response = render(request, 'petweb/index.html', context=context_dict)
    return response

def about(request):
    print(request.method)
    print(request.user)

    visitor_cookie_handler(request) 
    visits = request.session.get('visits', 1)

    context_dict = {'visits': visits }
    return render(request, 'petweb/about.html', context=context_dict)

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'petweb/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('/petweb/')
        else:
            print(form.errors)

    return render(request, 'petweb/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/petweb/')
    
    form = PageForm()
    if request.method =='POST':
        form = PageForm(request.POST)
        if form.is_valid():

            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('petweb:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    return render(request, 'petweb/add_page.html', {'form': form, 'category': category})

def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
        return HttpResponse("You are not logged in.")
    
@login_required
def restricted(request):
    return render(request, 'petweb/restricted.html')


def get_server_side_cookie(request, cookie, default_val=None): 
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits','1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                    '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def community(request):
    print(request.method)
    print(request.user)

    visitor_cookie_handler(request) 

    query = request.GET.get('q', '')  

    if query:
        posts = Post.objects.filter(title__icontains=query).order_by('-time') 
        users = User.objects.filter(username__icontains=query) 
    else:
        posts = Post.objects.all().order_by('-time')  
        users = []

    context_dict = {'posts': posts, 'users': users, 'query': query}  
    return render(request, 'petweb/community.html', context=context_dict)


def register(request):
    registered = False 

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)  
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()

            registered = True  
            user = authenticate(username=user_form.cleaned_data['username'], 
                                password=user_form.cleaned_data['password'])
            login(request, user)  
            return redirect('index') 

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    })

def user_profile(request, username):
    user = get_object_or_404(User, username=username) 
    profile= UserProfile.objects.get_or_create(user=user) 

    return render(request, 'petweb/user_profile.html', {'profile': profile, 'user': user})

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user 
            post.save()
            return redirect('petweb:community')
    else:
        form = PostForm()

    return render(request, 'petweb/create_post.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from petweb.models import Post, Comment

@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    all_comments = Comment.objects.filter(post=post).order_by("time")
    
    top_level_comments = all_comments.filter(replyee__isnull=True)

    reply_to = request.GET.get("reply_to", None)

    if request.method == "POST":
        content = request.POST.get("content")
        replyee_id = request.POST.get("replyee_id")

        if content:
            replyee = None
            if replyee_id:
                try:
                    replyee = Comment.objects.get(id=int(replyee_id))  
                except Comment.DoesNotExist:
                    replyee = None  

            Comment.objects.create(
                post=post,
                user=request.user,
                content=content,
                replyee=replyee 
            )

            return redirect('petweb:view_post', post_id=post.id)

    return render(request, "petweb/view_post.html", {
        "post": post,
        "top_level_comments": top_level_comments, 
        "all_comments": all_comments, 
        "reply_to": int(reply_to) if reply_to else None,
    })

def account(request):
    return render(request, 'petweb/account.html')