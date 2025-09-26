from django.urls import path
from .views import (
    MakaleListView, MakaleDetailView, MakaleCreateView, MakalelerimView,
    MakaleUpdateView, MakaleDeleteView, check_author_view, MakaleEkleRedirectView
)

urlpatterns = [
    # Public URLs
    path('', MakaleListView.as_view(), name='makale_list'),
    path('detay/<slug:slug>/', MakaleDetailView.as_view(), name='makale_detail'),
    path('makale-ekle/', MakaleEkleRedirectView.as_view(), name='makale_ekle_redirect'),
    path('yeni-ekle/', MakaleCreateView.as_view(), name='makale_ekle'),
    path('makalelerim/', MakalelerimView.as_view(), name='makalelerim'),
    path('duzenle/<slug:slug>/', MakaleUpdateView.as_view(), name='makale_duzenle'),
    path('sil/<slug:slug>/', MakaleDeleteView.as_view(), name='makale_sil'),
    path('check-author/', check_author_view, name='check_author'),
]
