from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('editor/', views.EditorPanelView.as_view(), name='editor_panel'),
    path('editor/duzenle/<slug:slug>/', views.EditorMakaleUpdateView.as_view(), name='editor_makale_duzenle'),
    path('users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('iletisim/', views.AdminIletisimListView.as_view(), name='admin_iletisim_list'),
    path('dergi-sayisi/', views.AdminDergiSayisiListView.as_view(), name='admin_dergisayisi_list'),
] 