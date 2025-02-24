import asyncio

from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from .models import Articles, Category, Author
from .forms import ArticleForm, RegisterUserForm, LoginUserForm
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
import logging
from django.views import View
from datetime import datetime
from asgiref.sync import sync_to_async

logger = logging.getLogger('main')


class NewsUpdateView(UpdateView):
    logger.info("NewsUpdateView")
    model = Articles  # Модель
    template_name = 'news/create.html'  # Шаблон
    form_class = ArticleForm

    def form_valid(self, form):
        return super().form_valid(form)


class NewsDeleteView(DeleteView):
    logger.info("NewsDeleteView")
    model = Articles  # Модель
    success_url = '/news/'
    template_name = 'news/news-delete.html'  # Шаблон


class NewDetailView(DetailView):
    logger.info("NewDetailView")
    model = Articles  # Модель
    template_name = 'news/details_view.html'  # Шаблон
    context_object_name = 'article'  # С помощью чего передаём данные

    # def get_queryset(self):
    #     #Articles.objects.filter(author = self.request.user)
    #     # sort_articles = Articles.objects.order_by("cat__name")
    #     # return sort_articles
    #     return Articles.objects.filter(authors__name="Дайан Сойер")


class RegisterUser(CreateView):
    logger.info("RegisterUser")
    form_class = RegisterUserForm
    template_name = 'news/register.html'
    success_url = reverse_lazy("login")


class LoginUser(LoginView):
    logger.info("LoginUser")
    form_class = LoginUserForm
    template_name = 'news/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


class Create(View):
    def get(self, request):
        logger.info("Create")
        error = ''
        form = ArticleForm()
        data = {
            'form': form,
            'error': error
        }
        return render(request, 'news/create.html', data)

    def post(self, request):
        logger.info("Create")
        error = ''
        form = ArticleForm(request.POST)  # Данные полученные от пользователя из формы

        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = "Форма была не верной"
            try:
                datetime.strptime(str(request.POST.get('date')), '%y/%m/%d %H:%M:%S')
            except:
                error = "Неверно введена дата и время"
        data = {
            'form': form,
            'error': error
        }
        return render(request, 'news/create.html', data)


class ShowCategory(View):

    def get(self, request, cat_id):
        logger.info("ShowCategory")
        news = asyncio.run(self.get_certain_articles(cat_id))
        cats = asyncio.run(self.get_all_categories())
        data = {
            'news': news,
            "cats": cats,
            "name_category": "Все категории"
        }
        return render(request, 'news/news_home.html', data)

    @sync_to_async
    def get_certain_articles(self, cat_id):
        return Articles.objects.filter(cat_id=cat_id)

    @sync_to_async
    def get_all_categories(self):
        return Category.objects.all()


class ShowAuthors(View):
    def get(self, request, authors_id):
        logger.info("ShowAuthors")

        authors = asyncio.run(self.get_id_authors(authors_id))
        data = {
            "authors": authors
        }
        return render(request, 'news/author_details.html', data)

    @sync_to_async
    def get_id_authors(self, authors_id):
        return Author.objects.filter(id=authors_id)


class LogoutUser(View):
    def get(self, request):
        logger.info("LogoutUser")
        logout(request)
        return redirect('login')


class AuthorsName(View):
    def get(self, request):
        logger.info("AuthorsName")
        authors = asyncio.run(self.get_all_authors())
        data = {
            "authors": authors
        }
        return render(request, 'news/author_names.html', data)

    @sync_to_async
    def get_all_authors(self):
        return Author.objects.all()


class NewsHome(View):
    def get(self, request):
        logger.info("NewsHome")
        news = asyncio.run(self.get_all_news())
        cats = asyncio.run(self.get_all_cats())
        sort_news_cats = asyncio.run(self.sort_cat_news())
        data = {
            'news': news,
            "cats": cats,
            "name_category": "Все категории",
            "sort_news_cats":sort_news_cats,
        }
        return render(request, 'news/news_home.html', data)

    @sync_to_async
    def get_all_news(self):
        return Articles.objects.all()

    @sync_to_async
    def get_all_cats(self):
        return Category.objects.all()

    @sync_to_async
    def sort_cat_news(self):
        return Articles.objects.order_by('cat__name')
