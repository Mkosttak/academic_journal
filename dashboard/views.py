from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST

from core.mixins import AdminRequiredMixin, EditorRequiredMixin
from users.models import User
from articles.models import Makale, DergiSayisi, DergiIcerigi
from pages.models import IletisimFormu
from articles.forms import EditorMakaleForm
from .forms import AdminUserUpdateForm, DergiSayisiForm

# Create your views here.

class EditorPanelView(EditorRequiredMixin, ListView):
    model = Makale
    template_name = 'dashboard/makale_yonetim_list.html'
    context_object_name = 'makaleler'
    paginate_by = 20

    def get_queryset(self):
        queryset = Makale.objects.all().select_related('dergi_sayisi').prefetch_related('yazarlar')
        
        # Filtreleme
        status = self.request.GET.get('status')
        if status == 'published':
            queryset = queryset.filter(goster_makaleler_sayfasinda=True)
        elif status == 'draft':
            queryset = queryset.filter(goster_makaleler_sayfasinda=False)
            
        # Arama
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(baslik__icontains=query) |
                Q(yazarlar__isim_soyisim__icontains=query) |
                Q(anahtar_kelimeler__icontains=query)
            ).distinct()

        # Özel sıralama: önce taslaklar, sonra yayındakiler, her ikisi de tarihe göre azalan
        if not status:
            taslaklar = queryset.filter(goster_makaleler_sayfasinda=False).order_by('-olusturulma_tarihi')
            yayinlar = queryset.filter(goster_makaleler_sayfasinda=True).order_by('-olusturulma_tarihi')
            from itertools import chain
            return list(chain(taslaklar, yayinlar))
        return queryset.order_by('-olusturulma_tarihi')

class EditorMakaleUpdateView(EditorRequiredMixin, UpdateView):
    model = Makale
    form_class = EditorMakaleForm
    template_name = 'dashboard/admin_makale_form.html'
    success_url = reverse_lazy('dashboard:editor_panel')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Makale Yönetimi (Editör)'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """
        View çalışmadan önce bu metot çalışır.
        SADECE editörlerin kendi makalelerini düzenlemesini engeller ve onları normal forma yönlendirir.
        Adminler bu kısıtlamadan muaftır.
        """
        makale = self.get_object()
        is_author = makale.yazarlar.filter(user_hesabi=request.user).exists()

        # Koşulu güncelliyoruz: Kullanıcı editör olmalı, ama admin olmamalı.
        if request.user.is_editor and not request.user.is_superuser and is_author:
            # Kullanıcı bir editör (ama admin değil) ve makalenin de yazarı ise,
            # kısıtlı düzenleme sayfasına yönlendir.
            return redirect('makale_duzenle', slug=makale.slug)

        # Yukarıdaki koşul sağlanmazsa (kullanıcı admin ise veya başkasının makalesini düzenliyorsa),
        # normal şekilde güçlü düzenleme sayfasını göster.
        return super().dispatch(request, *args, **kwargs)

# ----------------- YENİ ADMIN VIEW'LARI ---------------------------
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['toplam_kullanici'] = User.objects.count()
        context['toplam_makale'] = Makale.objects.count()
        context['cevap_bekleyen_mesaj'] = IletisimFormu.objects.filter(cevaplandi=False).count()
        context['yayindaki_makaleler'] = Makale.objects.filter(goster_makaleler_sayfasinda=True).count()
        context['son_makaleler'] = Makale.objects.all().order_by('-olusturulma_tarihi')[:5]
        context['son_kullanicilar'] = User.objects.all().order_by('-date_joined')[:5]
        context['en_cok_okunan_makaleler'] = Makale.objects.all().order_by('-goruntulenme_sayisi')[:5]
        return context

class AdminUserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin_user_list.html'
    context_object_name = 'kullanicilar'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | Q(email__icontains=query) |
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
        # Önce editörler, sonra editörler sayfasında gösterilenler, sonra diğerleri
        queryset = queryset.order_by(
            '-is_editor',
            '-goster_editorler_sayfasinda',
            '-date_joined'
        )
        return queryset

class AdminUserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = AdminUserUpdateForm
    template_name = 'dashboard/admin_user_form.html'
    success_url = reverse_lazy('dashboard:admin_user_list')

class AdminIletisimListView(AdminRequiredMixin, ListView):
    model = IletisimFormu
    template_name = 'dashboard/admin_iletisim_list.html'
    context_object_name = 'mesajlar'
    paginate_by = 15
    ordering = ['-olusturulma_tarihi']
    
    def get_queryset(self):
        queryset = IletisimFormu.objects.all()
        durum = self.request.GET.get('durum')
        if durum == 'cevaplandi': queryset = queryset.filter(cevaplandi=True)
        elif durum == 'cevaplanmadi': queryset = queryset.filter(cevaplandi=False)
        return queryset

@require_POST
def toggle_iletisim_status(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    mesaj = get_object_or_404(IletisimFormu, pk=pk)
    mesaj.cevaplandi = not mesaj.cevaplandi
    mesaj.save()
    return JsonResponse({'status': 'success', 'cevaplandi': mesaj.cevaplandi})

class AdminDergiSayisiListView(AdminRequiredMixin, ListView):
    model = DergiSayisi
    template_name = 'dashboard/admin_dergisayisi_list.html'
    context_object_name = 'dergi_sayilari'
    paginate_by = 20
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
        context['delete_message'] = (
            f"{self.object.get_tarih_format()} - {self.object.get_cilt_sayi_format()} dergi sayısını silmek üzeresiniz."
        )
        return context

class AdminIletisimSilView(AdminRequiredMixin, DeleteView):
    model = IletisimFormu
    template_name = 'dashboard/iletisim_confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin_iletisim_list')


# Dergi İçeriği Yönetimi Views
class AdminDergiIcerigiListView(AdminRequiredMixin, ListView):
    model = DergiIcerigi
    template_name = 'dashboard/admin_dergi_icerik_list.html'
    context_object_name = 'icerikler'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = DergiIcerigi.objects.all().select_related('dergi_sayisi').prefetch_related('yazarlar')
        
        # Filtreleme
        icerik_turu = self.request.GET.get('icerik_turu')
        if icerik_turu:
            queryset = queryset.filter(icerik_turu=icerik_turu)
            
        status = self.request.GET.get('status')
        if status == 'published':
            queryset = queryset.filter(yayinda_mi=True)
        elif status == 'draft':
            queryset = queryset.filter(yayinda_mi=False)
            
        # Arama
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(baslik__icontains=query) |
                Q(yazarlar__isim_soyisim__icontains=query) |
                Q(anahtar_kelimeler__icontains=query)
            ).distinct()

        return queryset.order_by('-olusturulma_tarihi')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['icerik_turleri'] = DergiIcerigi.ICERIK_TURLERI
        return context


class AdminDergiIcerigiCreateView(AdminRequiredMixin, CreateView):
    model = DergiIcerigi
    template_name = 'dashboard/admin_dergi_icerik_form.html'
    fields = ['baslik', 'aciklama', 'pdf_dosyasi', 'dergi_sayisi', 'yayinda_mi']
    success_url = reverse_lazy('dashboard:admin_dergi_icerik_list')
    
    def form_valid(self, form):
        form.instance.olusturan_admin = self.request.user
        return super().form_valid(form)


class AdminDergiIcerigiUpdateView(AdminRequiredMixin, UpdateView):
    model = DergiIcerigi
    template_name = 'dashboard/admin_dergi_icerik_form.html'
    fields = ['baslik', 'aciklama', 'pdf_dosyasi', 'dergi_sayisi', 'yayinda_mi']
    success_url = reverse_lazy('dashboard:admin_dergi_icerik_list')


class AdminDergiIcerigiDeleteView(AdminRequiredMixin, DeleteView):
    model = DergiIcerigi
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard:admin_dergi_icerik_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_message'] = (
            f"{self.object.get_icerik_turu_display()} - {self.object.baslik} içeriğini silmek üzeresiniz."
        )
        return context


class AdminDergiIcerigiDetailView(AdminRequiredMixin, DetailView):
    model = DergiIcerigi
    template_name = 'dashboard/admin_dergi_icerik_detail.html'
    context_object_name = 'icerik'
