from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Create your views here.

class KayitOlView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/kayit_ol.html'
    success_url = reverse_lazy('login')

class GirisYapView(LoginView):
    template_name = 'registration/login.html'
    success_url = '/'  # veya reverse_lazy('anasayfa')



class ParolaDegistirView(PasswordChangeView):
    template_name = 'registration/parola_degistir.html'
    success_url = reverse_lazy('profil')

class ProfilView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profil.html'
    context_object_name = 'profil_kullanici'

    def get_object(self, queryset=None):
        # Eğer URL'de bir 'username' parametresi varsa o kullanıcıyı, yoksa giriş yapanı göster
        username = self.kwargs.get('username')
        if username:
            return User.objects.get(username=username)
        return self.request.user

class ProfilDuzenleView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/profil_duzenle.html'
    success_url = reverse_lazy('profil')

    def get_object(self, queryset=None):
        # Kullanıcı sadece kendi profilini düzenleyebilir
        return self.request.user
