from django.urls import path, re_path
from .views import RandomFactsListView, RandomFactIds, RandomFactDetailView, TranslatedFactDetailView

urlpatterns = [
    path('status/', RandomFactsListView.as_view()),
    path('facts/', RandomFactIds.as_view()),
    path('facts/<slug>/', RandomFactDetailView.as_view()),
    path('facts/<slug:id>/lang=<slug:lang>/', TranslatedFactDetailView.as_view()),
]