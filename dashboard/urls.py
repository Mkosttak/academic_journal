# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Admin Ana Panel
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),

    # Editör & Admin Makale Yönetimi
    path('editor/', views.EditorPanelView.as_view(), name='editor_panel'),
    path('editor/duzenle/<slug:slug>/', views.EditorMakaleUpdateView.as_view(), name='editor_makale_duzenle'),

    # Admin - Kullanıcı Yönetimi
    path('users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('users/edit/<int:pk>/', views.AdminUserUpdateView.as_view(), name='admin_user_update'),

    # Admin - İletişim Yönetimi
    path('iletisim/', views.AdminIletisimListView.as_view(), name='admin_iletisim_list'),
    path('iletisim/toggle-status/<int:pk>/', views.toggle_iletisim_status, name='toggle_iletisim_status'),
    path('iletisim/sil/<int:pk>/', views.AdminIletisimSilView.as_view(), name='admin_iletisim_sil'),

    # Admin - Dergi Sayısı Yönetimi
    path('dergi-sayilari/', views.AdminDergiSayisiListView.as_view(), name='admin_dergisayisi_list'),
    path('dergi-sayilari/yeni/', views.AdminDergiSayisiCreateView.as_view(), name='admin_dergisayisi_create'),
    path('dergi-sayilari/duzenle/<int:pk>/', views.AdminDergiSayisiUpdateView.as_view(), name='admin_dergisayisi_update'),
    path('dergi-sayilari/sil/<int:pk>/', views.AdminDergiSayisiDeleteView.as_view(), name='admin_dergisayisi_delete'),
]