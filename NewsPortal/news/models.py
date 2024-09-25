from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from django import forms


class Author(models.Model):
    authors = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        article_rating_author = 0
        articles = Post.objects.filter(author=self)
        for p in articles:
            article_rating_author += p.article_rating
        rating_comment_author = 0
        comments = Comment.objects.filter(users=self.authors)
        for c in comments:
            rating_comment_author += c.comment_rating
        comment_post_rating = 0
        post_comments = Comment.objects.filter(post__author=self)
        for a in post_comments:
            comment_post_rating += a.comment_rating
        self.rating = article_rating_author * 3 + rating_comment_author + comment_post_rating
        self.save()


class Category(models.Model):
    topic = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.topic.title()


TYPE_TEXT = [
    ("NEWS", "Новость"),
    ("ARTI", "Статья")
]


class Post(models.Model):
    article_rating = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    text = models.TextField()
    title_post = models.CharField(max_length=50)
    time_in = models.DateTimeField(auto_now_add=True)
    type_text = models.CharField(max_length=10, choices=TYPE_TEXT)

    def like(self):
        self.article_rating += 1
        self.save()

    def dislike(self):
        self.article_rating -=1
        self.save()

    def preview(self):
        start_post = self.text[:124] + "..."

    def __str__(self):
        return f'{self.title_post.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscribers = models.ManyToManyField(User, blank=True)


class Comment(models.Model):
    post = models.authors = models.ForeignKey(Post, on_delete=models.CASCADE)
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    text_comment = models.TextField()
    time_in_comment = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -=1
        self.save()


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )