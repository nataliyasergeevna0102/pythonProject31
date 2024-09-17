from os import path

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy, resolve
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from .forms import PostForm
from .models import Post, BaseRegisterForm, Category
from .filters import PostFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings

DEFAULT_FROM_EMAIL=settings.DEFAULT_FROM_EMAIL


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


class PostCategoryView(ListView):
    model = Post
    template_name = 'category.html'
    context_object_name = "posts"
    ordering = ['_created_at']
    paginate_by = 10

    def get_queryset(self):
        self.id = (resolve(self.request.path_info).kwargs['pk'])
        c = Category.objects.get(id=self.id)
        queryset = Post.objects.filter (category=c)
        return queryset

    def get_content_data(self, **kwargs):
        content = super().get_content_data(**kwargs)
        user=self.request.user
        category=Category.objects.get(id=self.id)
        subscribed=category.subscribers.filter(email=user.email)
        if not subscribed:
            content['category']=category
        return content


@login_required
def subscribe_to_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    email = user.email
    if not category.subscribers.filter(id=user.id).exists():
        category.subscribers.add(user)
        html=render_to_string(
            'mail/subscribed.html',
            {
                'category':category,
                'user':user,
            },
        )
        msg=EmailMultiAlternatives(
            subject=f'{category} subscription',
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[email,],
        )
        msg.attach_alternative(html, 'text/html')

        try:
            msg.send()
        except Exception as e:
            print(e)
        return redirect('HTTP_REFERER')

