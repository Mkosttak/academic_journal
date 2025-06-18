from django.urls import path
from .views import AnasayfaView, HakkindaView, IletisimView, EditorlerListView

urlpatterns = [
    path('', AnasayfaView.as_view(), name='anasayfa'),
    path('hakkinda/', HakkindaView.as_view(), name='hakkinda'),
    path('iletisim/', IletisimView.as_view(), name='iletisim'),
    path('editorler/', EditorlerListView.as_view(), name='editorler'),
]
