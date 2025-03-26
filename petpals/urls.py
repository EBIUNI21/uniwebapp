from django.urls import path
from django.contrib.auth.views import LogoutView
from petpals import views

app_name = 'petpals' 


urlpatterns = [path('', views.index, name='index'),
               path('about/', views.about, name='about'),
               path('category/<slug:category_name_slug>/add_page/', views.add_page,name='add_page'),
               path('category/<slug:category_name_slug>/', views.show_category,name='show_category'),
               path('add_category/', views.add_category, name='add_category'),
               path('restricted/', views.restricted, name='restricted'),
               path('register/', views.register, name='register'),
               path('accounts/logout/', LogoutView.as_view(), name='auth_logout'),
               path('community/', views.community, name='community'),
               path('community/create_post/', views.create_post, name='create_post'),
               path('community/post/<int:post_id>/', views.view_post, name='view_post'),
               path('account/', views.account, name='account'),
               path('goto/', views.goto_url, name='goto'),
               path('like/', views.like_post, name='like_post'),
               path('account/edit/', views.edit_profile, name='edit_profile')


]