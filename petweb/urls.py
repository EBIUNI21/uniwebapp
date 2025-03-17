from django.urls import path
from django.contrib.auth.views import LogoutView
from petweb import views

app_name = 'petweb' 


urlpatterns = [path('', views.index, name='index'),
               path('about/', views.about, name='about'),
               path('category/<slug:category_name_slug>/add_page/', views.add_page,name='add_page'),
               path('category/<slug:category_name_slug>/', views.show_category,name='show_category'),
               path('add_category/', views.add_category, name='add_category'),
               path('restricted/', views.restricted, name='restricted'),
               path('register/', views.register, name='register'),
               path('accounts/logout/', LogoutView.as_view(), name='auth_logout'),
               path('community/', views.community, name='community'),
               path('profile/<str:username>/', views.user_profile, name='user_profile'), 
               path('community/create_post/', views.create_post, name='create_post'),
               path('community/post/<int:post_id>/', views.view_post, name='view_post'),
               path('account/', views.account, name='account'),
]