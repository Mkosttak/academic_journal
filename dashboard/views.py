from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

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
        
        # Temel istatistikler
        context['toplam_kullanici'] = User.objects.count()
        context['toplam_makale'] = Makale.objects.count()
        context['toplam_dergi_sayisi'] = DergiSayisi.objects.count()
        context['toplam_icerik'] = DergiIcerigi.objects.count()
        context['cevap_bekleyen_mesaj'] = IletisimFormu.objects.filter(cevaplandi=False).count()
        context['yayindaki_makaleler'] = Makale.objects.filter(goster_makaleler_sayfasinda=True).count()
        context['yayindaki_icerikler'] = DergiIcerigi.objects.filter(yayinda_mi=True).count()
        
        # Son eklenenler
        context['son_makaleler'] = Makale.objects.select_related('dergi_sayisi').prefetch_related('yazarlar').order_by('-olusturulma_tarihi')[:5]
        context['son_icerikler'] = DergiIcerigi.objects.select_related('dergi_sayisi').prefetch_related('yazarlar').order_by('-olusturulma_tarihi')[:5]
        context['son_dergi_sayilari'] = DergiSayisi.objects.order_by('-olusturulma_tarihi')[:5]
        context['son_kullanicilar'] = User.objects.all().order_by('-date_joined')[:5]
        
        # En çok okunanlar
        context['en_cok_okunan_makaleler'] = Makale.objects.filter(goster_makaleler_sayfasinda=True).order_by('-goruntulenme_sayisi')[:5]
        
        # Bu ay istatistikleri
        from django.utils import timezone
        from datetime import datetime, timedelta
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        context['bu_ay_makale'] = Makale.objects.filter(olusturulma_tarihi__gte=this_month_start).count()
        context['bu_ay_icerik'] = DergiIcerigi.objects.filter(olusturulma_tarihi__gte=this_month_start).count()
        context['bu_ay_kullanici'] = User.objects.filter(date_joined__gte=this_month_start).count()
        
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

        return queryset.order_by('dergi_sayisi__yil', 'dergi_sayisi__ay', 'dergi_sayisi__sayi_no', 'siralama', '-olusturulma_tarihi')
    
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

# Makale Sıralama Views
class AdminMakaleSiralamaView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_makale_siralama.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dergi_sayisi_id = self.kwargs.get('dergi_sayisi_id')
        
        try:
            dergi_sayisi = DergiSayisi.objects.get(id=dergi_sayisi_id)
            # Önce sıralamaya göre, sonra oluşturulma tarihine göre sırala
            makaleler = Makale.objects.filter(dergi_sayisi=dergi_sayisi).order_by('siralama', '-olusturulma_tarihi')
            icerikler = DergiIcerigi.objects.filter(dergi_sayisi=dergi_sayisi).order_by('siralama', '-olusturulma_tarihi')
            
            # Tüm içerikleri birleştir ve sırala
            all_items = []
            for makale in makaleler:
                all_items.append({
                    'id': makale.id,
                    'type': 'makale',
                    'siralama': makale.siralama,
                    'obj': makale
                })
            for icerik in icerikler:
                all_items.append({
                    'id': icerik.id,
                    'type': 'icerik', 
                    'siralama': icerik.siralama,
                    'obj': icerik
                })
            
            # Sıralamaya göre sırala
            all_items.sort(key=lambda x: x['siralama'])
            
            # Sıralanmış listeleri oluştur
            sorted_makaleler = [item['obj'] for item in all_items if item['type'] == 'makale']
            sorted_icerikler = [item['obj'] for item in all_items if item['type'] == 'icerik']
            
            context.update({
                'dergi_sayisi': dergi_sayisi,
                'makaleler': sorted_makaleler,
                'icerikler': sorted_icerikler,
                'all_items': all_items,
                'page_title': f'İçerik Sıralaması - {dergi_sayisi}',
            })
        except DergiSayisi.DoesNotExist:
            context['error'] = 'Dergi sayısı bulunamadı.'
            
        return context

@login_required
@require_POST
def update_makale_order_dashboard(request):
    """
    Dashboard'dan makalelerin sıralamasını günceller. Sadece admin kullanıcıları kullanabilir.
    """
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Bu işlem için admin yetkisi gereklidir.'}, status=403)
    
    try:
        data = json.loads(request.body)
        dergi_sayisi_id = data.get('dergi_sayisi_id')
        article_orders = data.get('article_orders', [])
        
        if not dergi_sayisi_id or not article_orders:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz veri.'}, status=400)
        
        # Dergi sayısını kontrol et
        try:
            dergi_sayisi = DergiSayisi.objects.get(id=dergi_sayisi_id)
        except DergiSayisi.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Dergi sayısı bulunamadı.'}, status=404)
        
        # Makalelerin sıralamasını güncelle
        for order_data in article_orders:
            article_id = order_data.get('id')
            new_order = order_data.get('order')
            
            if article_id is not None and new_order is not None:
                try:
                    article = Makale.objects.get(id=article_id, dergi_sayisi=dergi_sayisi)
                    article.siralama = new_order
                    article.save(update_fields=['siralama'])
                except Makale.DoesNotExist:
                    continue  # Makale bulunamadı, devam et
        
        return JsonResponse({'status': 'success', 'message': 'Sıralama başarıyla güncellendi.'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON verisi.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Bir hata oluştu: {str(e)}'}, status=500)

# Dergi İçeriği Sıralama Views
class AdminDergiIcerikSiralamaView(AdminRequiredMixin, TemplateView):
    template_name = 'dashboard/admin_dergi_icerik_siralama.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dergi_sayisi_id = self.kwargs.get('dergi_sayisi_id')
        
        try:
            dergi_sayisi = DergiSayisi.objects.get(id=dergi_sayisi_id)
            icerikler = DergiIcerigi.objects.filter(dergi_sayisi=dergi_sayisi).order_by('siralama', '-olusturulma_tarihi')
            
            context.update({
                'dergi_sayisi': dergi_sayisi,
                'icerikler': icerikler,
                'page_title': f'Dergi İçeriği Sıralaması - {dergi_sayisi}',
            })
        except DergiSayisi.DoesNotExist:
            context['error'] = 'Dergi sayısı bulunamadı.'
            
        return context

@login_required
@require_POST
def update_dergi_icerik_order_dashboard(request):
    """
    Dashboard'dan dergi içeriklerinin sıralamasını günceller. Sadece admin kullanıcıları kullanabilir.
    """
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Bu işlem için admin yetkisi gereklidir.'}, status=403)
    
    try:
        data = json.loads(request.body)
        dergi_sayisi_id = data.get('dergi_sayisi_id')
        content_orders = data.get('content_orders', [])
        
        if not dergi_sayisi_id or not content_orders:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz veri.'}, status=400)
        
        # Dergi sayısını kontrol et
        try:
            dergi_sayisi = DergiSayisi.objects.get(id=dergi_sayisi_id)
        except DergiSayisi.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Dergi sayısı bulunamadı.'}, status=404)
        
        # İçeriklerin sıralamasını güncelle
        for order_data in content_orders:
            content_id = order_data.get('id')
            new_order = order_data.get('order')
            
            if content_id is not None and new_order is not None:
                try:
                    icerik = DergiIcerigi.objects.get(id=content_id, dergi_sayisi=dergi_sayisi)
                    icerik.siralama = new_order
                    icerik.save(update_fields=['siralama'])
                except DergiIcerigi.DoesNotExist:
                    continue  # İçerik bulunamadı, devam et
        
        return JsonResponse({'status': 'success', 'message': 'Sıralama başarıyla güncellendi.'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON verisi.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Bir hata oluştu: {str(e)}'}, status=500)
