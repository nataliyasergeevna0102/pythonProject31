from django.urls import path
from .views import (PostList, PostDetail, PostSearch, PostCreate, PostUpdate, PostDelete,
                    upgrade_me, IndexView, subscribe_to_category, PostCategoryView)
from .views import BaseRegisterView

urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>', PostDetail.as_view()),
    path('news/search', PostSearch.as_view()),
    path('news/create/', PostCreate.as_view(), name='post_create'),
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
    path('news/<int:pk>/delete', PostDelete.as_view(), name='post_delete'),
    path('article/create/', PostCreate.as_view(), name='post_create'),
    path('article/<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
    path('article/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('signup/', BaseRegisterView.as_view(template_name = 'signup.html'), name='signup'),
    path('upgrade/', upgrade_me, name = 'upgrade'),
    path('user', IndexView.as_view()),
    path('subscribe/<int:pk>/', subscribe_to_category, name='subscribers'),
    path('category/<int:pk>/', PostCategoryView.as_view(), name='category'),
]