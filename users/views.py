from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.db.models import Sum
from articles.models import Yazar

User = get_user_model()

# Create your views here.

class KayitOlView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/kayit_ol.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
        return response

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class GirisYapView(LoginView):
    template_name = 'registration/login.html'
    success_url = '/'  # veya reverse_lazy('anasayfa')

    def form_valid(self, form):
        """Kullanıcı giriş yaptığında mesaj gösterir."""
        from core.rate_limiting import BruteForceProtection, RateLimiter
        # Başarılı login kaydet
        username = form.cleaned_data.get('username')
        ip = RateLimiter.get_client_ip(self.request)
        BruteForceProtection.record_successful_login(username, ip)
        
        messages.success(self.request, f"Hoş geldiniz, {form.get_user().get_full_name() or form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Form geçersiz olduğunda hata mesajları gösterir."""
        from django.shortcuts import redirect
        from django.urls import reverse
        from core.rate_limiting import BruteForceProtection, RateLimiter
        
        # Başarısız login kaydet
        username = form.cleaned_data.get('username', '')
        ip = RateLimiter.get_client_ip(self.request)
        BruteForceProtection.record_failed_login(username, ip)
        
        # Hata durumunda aynı sayfaya error parametresi ile redirect yap
        return redirect(f"{reverse('login')}?error=1")
    
    def post(self, request, *args, **kwargs):
        """POST isteğini işler ve debug bilgisi ekler."""
        print(f"POST isteği alındı: {request.method}")
        print(f"Form data: {request.POST}")
        return super().post(request, *args, **kwargs)

class CikisYapView(LogoutView):
    next_page = reverse_lazy('anasayfa')

class ParolaDegistirView(PasswordChangeView):
    template_name = 'registration/parola_degistir.html'
    success_url = reverse_lazy('my_profil')

    def form_valid(self, form):
        messages.success(self.request, 'Parolanız başarıyla değiştirildi.')
        return super().form_valid(form)

class MyProfilView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/my_profil.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            yazar = self.request.user.yazar_profili
            makaleler = yazar.makaleler.order_by('-guncellenme_tarihi')
        except Exception:
            makaleler = []
        context['last_articles'] = makaleler[:3]
        context['published_count'] = makaleler.filter(goster_makaleler_sayfasinda=True).count() if hasattr(makaleler, 'filter') else 0
        return context

class ProfilView(DetailView):
    model = User
    template_name = 'pages/editor_profile.html'
    context_object_name = 'profil_kullanici'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        yazar_profili = self.get_object().yazar_profili if hasattr(self.get_object(), 'yazar_profili') else None
        if yazar_profili:
            context['makaleler'] = yazar_profili.makaleler.filter(goster_makaleler_sayfasinda=True).order_by('-olusturulma_tarihi')
        else:
            context['makaleler'] = []
        return context

class ProfilDuzenleView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/profil_duzenle.html'
    success_url = reverse_lazy('my_profil')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # Özgeçmiş kaldırma flag'i kontrolü
        if self.request.POST.get('remove_resume') == '1':
            if self.object.resume:
                self.object.resume.delete(save=False)
                self.object.resume = None
                self.object.save()
        messages.success(self.request, 'Profil bilgileriniz başarıyla güncellendi.')
        return super().form_valid(form)
