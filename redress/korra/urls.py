from . import views
from django.urls import path

app_name = 'korra'
urlpatterns = [
    path('', views.dex, name='dex'),
    # ex: /korra/5/
    path('specifics/<int:question_id>/', views.detail, name='detail'),
    # ex: /korra/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /korra/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
