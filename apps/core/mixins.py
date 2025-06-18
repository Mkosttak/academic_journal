from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home')

class EditorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_editor or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home')

class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_author or self.request.user.is_editor or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home') 