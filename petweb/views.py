from django.shortcuts import render, get_object_or_404, redirect
from petweb.models import Category, Page
from petweb.forms import PageForm, CategoryForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from petweb.models import Post, Comment, UserProfile, Like
from petweb.forms import PostForm, CommentForm
from petweb.forms import UserForm, UserProfileForm
from django.contrib.auth.models import User 
from django.http import JsonResponse


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

@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    post.views += 1
    post.save()

    all_comments = Comment.objects.filter(post=post).order_by("time")
    top_level_comments = all_comments.filter(replyee__isnull=True)

    reply_to = request.GET.get("reply_to", None)

    user_has_liked = post.like_set.filter(user=request.user).exists()

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
        
    context = {
        "post": post,
        "top_level_comments": top_level_comments,
        "all_comments": all_comments,
        "reply_to": int(reply_to) if reply_to else None,
        "user_has_liked": user_has_liked,  # Pass this to the template
    }
    return render(request, "petweb/view_post.html", context)

@login_required
def like_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        user = request.user

        post = Post.objects.get(id=post_id)

        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()
            is_liked = False
        else:
            is_liked = True

        like_count = post.like_set.count()
        return JsonResponse({'is_liked': is_liked, 'like_count': like_count})

@login_required
def account(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('petweb:account')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        "form": form,
    }
    return render(request, 'petweb/account.html', context)

def goto_url(request):
    page_id = request.GET.get('page_id')
    if page_id:
        try:
            page = Page.objects.get(id=page_id)
            page.views += 1
            page.save()
            return redirect(page.url)
        except Page.DoesNotExist:
            pass
    return redirect(reverse('petweb:index'))