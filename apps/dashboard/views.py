from django.shortcuts import render
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from apps.core.mixins import AdminRequiredMixin, EditorRequiredMixin
from apps.users.models import User
from apps.articles.models import Makale, DergiSayisi
from apps.pages.models import IletisimFormu
from apps.articles.forms import EditorMakaleForm
from .forms import AdminUserUpdateForm, DergiSayisiForm

# Create your views here.

class EditorPanelView(EditorRequiredMixin, ListView):
    model = Makale
    template_name = 'articles/editor_panel.html'
    context_object_name = 'makaleler'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status == 'published':
            queryset = queryset.filter(yayinda=True)
        elif status == 'draft':
            queryset = queryset.filter(yayinda=False)
        return queryset.order_by('-olusturulma_tarihi')

class EditorMakaleUpdateView(EditorRequiredMixin, UpdateView):
    model = Makale
    form_class = EditorMakaleForm
    template_name = 'dashboard/makale_form.html'
    success_url = reverse_lazy('dashboard:editor_panel')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Makale Yönetimi (Editör)'
        return context

# ----------------- YENİ ADMIN VIEW'LARI ---------------------------
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['toplam_kullanici'] = User.objects.count()
        context['toplam_makale'] = Makale.objects.count()
        context['cevap_bekleyen_mesaj'] = IletisimFormu.objects.filter(cevaplandi=False).count()
        context['yayindaki_makaleler'] = Makale.objects.filter(yayinda=True).count()
        context['son_makaleler'] = Makale.objects.all().order_by('-olusturulma_tarihi')[:5]
        return context

class AdminUserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin_user_list.html'
    context_object_name = 'users'
    paginate_by = 10

class AdminUserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = AdminUserUpdateForm
    template_name = 'dashboard/admin_user_form.html'
    success_url = reverse_lazy('dashboard:admin_user_list')

class AdminIletisimListView(AdminRequiredMixin, ListView):
    model = IletisimFormu
    template_name = 'dashboard/admin_iletisim_list.html'
    context_object_name = 'mesajlar'
    paginate_by = 10
    ordering = ['-olusturulma_tarihi']

class AdminIletisimDetailView(AdminRequiredMixin, DetailView):
    model = IletisimFormu
    template_name = 'dashboard/admin_iletisim_detail.html'
    context_object_name = 'mesaj'

def toggle_iletisim_status(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    mesaj = get_object_or_404(IletisimFormu, pk=pk)
    mesaj.cevaplandi = not mesaj.cevaplandi
    mesaj.save()
    return JsonResponse({'status': 'success', 'cevaplandi': mesaj.cevaplandi})

class AdminDergiSayisiListView(AdminRequiredMixin, ListView):
    model = DergiSayisi
    template_name = 'dashboard/admin_dergisayisi_list.html'
    context_object_name = 'dergi_sayilari'
    paginate_by = 10
    ordering = ['-olusturulma_tarihi']

class AdminDergiSayisiCreateView(AdminRequiredMixin, CreateView):
    model = DergiSayisi
    form_class = DergiSayisiForm
    template_name = 'dashboard/admin_dergisayisi_form.html'
    success_url = reverse_lazy('dashboard:admin_dergisayisi_list')

class AdminDergiSayisiUpdateView(AdminRequiredMixin, UpdateView):
    model = DergiSayisi
    form_class = DergiSayisiForm
    template_name = 'dashboard/admin_dergisayisi_form.html'
    success_url = reverse_lazy('dashboard:admin_dergisayisi_list')

class AdminDergiSayisiDeleteView(AdminRequiredMixin, DeleteView):
    model = DergiSayisi
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin_dergisayisi_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_message'] = f"'{self.object.sayi}' isimli dergi sayısını silmek üzeresiniz."
        return context
