from django.urls import path
from .views import AnasayfaView, IletisimView, EditorlerListView

urlpatterns = [
    path('', AnasayfaView.as_view(), name='anasayfa'),
    path('iletisim/', IletisimView.as_view(), name='iletisim'),
    path('editorler/', EditorlerListView.as_view(), name='editorler'),
]
