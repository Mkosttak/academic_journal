# core/mixins.py

from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from articles.models import Makale

class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, 'Bu sayfaya erişim için admin yetkisi gerekmektedir.')
            return redirect('anasayfa')
        return super().dispatch(request, *args, **kwargs)

class EditorRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_editor or request.user.is_superuser):
            messages.error(request, 'Bu sayfaya erişim için editör yetkisi gerekmektedir.')
            return redirect('anasayfa')
        return super().dispatch(request, *args, **kwargs)

class AuthorRequiredMixin(AccessMixin):
    """
    Kullanıcının, makalenin yazarlarından biri olup olmadığını kontrol eder.
    Admin ve Editörlere her zaman izin verir.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        slug = kwargs.get('slug')
        makale = get_object_or_404(Makale, slug=slug)

        is_author = makale.yazarlar.filter(user_hesabi=request.user).exists()
        is_privileged = request.user.is_editor or request.user.is_superuser

        if not (is_author or is_privileged):
            messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
            return redirect('anasayfa')
            
        return super().dispatch(request, *args, **kwargs)