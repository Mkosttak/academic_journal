from django.urls import path
from .views import (
    MakaleListView, MakaleDetailView, MakaleCreateView, MakalelerimView,
    MakaleUpdateView, MakaleDeleteView
)

urlpatterns = [
    # Public URLs
    path('', MakaleListView.as_view(), name='makale_list'),
    path('detay/<slug:slug>/', MakaleDetailView.as_view(), name='makale_detail'),
    
    # Author specific URLs
    path('yeni-ekle/', MakaleCreateView.as_view(), name='makale_ekle'),
    path('makalelerim/', MakalelerimView.as_view(), name='makalelerim'),
    path('duzenle/<slug:slug>/', MakaleUpdateView.as_view(), name='makale_duzenle'),
    path('sil/<slug:slug>/', MakaleDeleteView.as_view(), name='makale_sil'),
]
