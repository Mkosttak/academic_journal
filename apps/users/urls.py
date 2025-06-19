from django.urls import path
from .views import (
    KayitOlView, GirisYapView, CikisYapView, ParolaDegistirView,
    ProfilView, ProfilDuzenleView, MyProfilView
)

urlpatterns = [
    path('kayit-ol/', KayitOlView.as_view(), name='kayit_ol'),
    path('giris/', GirisYapView.as_view(), name='login'), # Django'nun beklediği isim 'login'
    path('cikis/', CikisYapView.as_view(), name='logout'),
    path('parola-degistir/', ParolaDegistirView.as_view(), name='parola_degistir'),
    
    path('profil/duzenle/', ProfilDuzenleView.as_view(), name='profil_duzenle'),
    path('my-profil/', MyProfilView.as_view(), name='my_profil'),
    
    # Bu URL, belirli bir kullanıcının profilini gösterir (Editörler sayfasından tıklanınca)
    path('profil/<str:username>/', ProfilView.as_view(), name='kullanici_profili'), 
]
