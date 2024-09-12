from os import path

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from .forms import PostForm
from .models import Post, BaseRegisterForm
from .filters import PostFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin

# Create your views here.
class PostList(ListView):
    model = Post
    ordering = 'title_post'
    template_name = 'flatpages/post_list.html'
    context_object_name = 'post'
    order_by = '- time_in'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'protect/post_detail.html'
    context_object_name = 'post'


class PostSearch(ListView):
    model = Post
    template_name = 'protect/search_list.html'
    context_object_name = 'post'
    order_by = '- time_in'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        if self.request.GET:
            return self.filterset.qs
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PostCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news_add_post',)
    form_class = PostForm
    model = Post
    template_name = 'protect/edit_form.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if path == 'news/create/':
            post.type_text = "NEWS"
        if path == 'article/create/':
            post.type_text = "ARTI"
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news_change_post',)
    form_class = PostForm
    model = Post
    template_name = 'protect/edit_form.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if path == 'news/<int:pk>/edit':
            post.type_text = "NEWS"
        if path == 'article/<int:pk>/edit':
            post.type_text = "ARTI"
        return super().form_valid(form)


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'protect/post_confirm_delete.html'
    success_url = reverse_lazy('post_delete')

    def form_valid(self, form):
        post = form.save(commit=False)
        if path == 'news/<int:pk>/delete':
            post.type_text = "NEWS"
        if path == 'article/<int:pk>/delete':
            post.type_text = "ARTI"
        return super().form_valid(form)


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


class CommonSignupForm(SignupForm):

    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


