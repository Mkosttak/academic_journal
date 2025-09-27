from django.urls import path
from .views import AnasayfaView, IletisimView, EditorlerListView, SayilarListView, SayiMakaleleriView

urlpatterns = [
    path('', AnasayfaView.as_view(), name='anasayfa'),
    path('iletisim/', IletisimView.as_view(), name='iletisim'),
    path('editorler/', EditorlerListView.as_view(), name='editorler'),
    path('sayilar/', SayilarListView.as_view(), name='sayilar'),
    path('sayilar/<slug:slug>/', SayiMakaleleriView.as_view(), name='sayi_makaleleri'),
]
