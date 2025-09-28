from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Makale, DergiSayisi
from .forms import MakaleForm
from core.mixins import AdminRequiredMixin, AuthorRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from users.models import User
import re
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

# Create your views here.

class MakaleEkleRedirectView(View):
    """
    Makale Ekle butonuna tıklandığında giriş yapmamış kullanıcıları 
    login sayfasına yönlendirir ve mesaj gösterir.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('makale_ekle')
        else:
            messages.info(
                request, 
                '📝 Makale eklemek için önce giriş yapmanız gerekmektedir. '
                'Giriş yaptıktan sonra direkt makale ekleme sayfasına yönlendirileceksiniz.'
            )
            # next parametresi ile giriş sonrası makale ekleme sayfasına yönlendir
            from django.urls import reverse
            login_url = reverse('login') + '?next=' + reverse('makale_ekle')
            return redirect(login_url)

class MakaleListView(ListView):
    model = Makale
    template_name = 'articles/makale_list.html'
    context_object_name = 'makaleler'
    paginate_by = 10

    def get_queryset(self):
        # Sadece yayında olan makaleleri göster - Optimized queries
        queryset = Makale.objects.filter(
            goster_makaleler_sayfasinda=True
        ).select_related('dergi_sayisi').prefetch_related(
            'yazarlar',
            'yazarlar__user_hesabi'  # Yazar kullanıcı bilgilerini de prefetch et
        )
        
        # Filtreleme ve Arama
        dergi_no = self.request.GET.get('dergi')
        query = self.request.GET.get('q')

        if dergi_no:
            queryset = queryset.filter(dergi_sayisi__id=dergi_no)
        if query:
            queryset = queryset.filter(
                Q(baslik__icontains=query) |
                Q(yazarlar__isim_soyisim__icontains=query) |
                Q(anahtar_kelimeler__icontains=query)
            ).distinct()
        
        # Sıralama: önce dergi sayısına göre, sonra makale sıralamasına göre
        queryset = queryset.order_by('dergi_sayisi__yil', 'dergi_sayisi__ay', 'dergi_sayisi__sayi_no', 'siralama', '-olusturulma_tarihi')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dergi sayılarını da optimize et
        context['dergi_sayilari'] = DergiSayisi.objects.filter(
            yayinlandi_mi=True
        ).select_related().prefetch_related('makaleler').order_by('-yil', '-ay', '-sayi_no')
        return context

class MakaleDetailView(DetailView):
    model = Makale
    template_name = 'articles/makale_detail.html'
    context_object_name = 'makale'

    def get_object(self, queryset=None):
        # Eğer dergi_slug parametresi varsa, o dergiye ait makaleyi bul
        if 'dergi_slug' in self.kwargs:
            dergi_slug = self.kwargs['dergi_slug']
            makale_slug = self.kwargs['makale_slug']
            
            try:
                from .models import DergiSayisi
                dergi_sayisi = DergiSayisi.objects.get(slug=dergi_slug)
                obj = Makale.objects.get(slug=makale_slug, dergi_sayisi=dergi_sayisi)
            except (DergiSayisi.DoesNotExist, Makale.DoesNotExist):
                from django.http import Http404
                raise Http404("Makale bulunamadı.")
        else:
            # Normal slug ile makaleyi bul
            obj = super().get_object(queryset=queryset)
        
        # Görüntülenme sayısını artır
        obj.goruntulenme_sayisi += 1
        obj.save(update_fields=['goruntulenme_sayisi'])
        return obj

class MakaleCreateView(LoginRequiredMixin, CreateView):
    model = Makale
    form_class = MakaleForm
    template_name = 'articles/makale_form.html'
    success_url = reverse_lazy('makalelerim')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Yeni Makale'
        context['submit_text'] = 'Makale Oluştur'
        return context

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, 'Makaleniz başarıyla oluşturuldu ve incelenmek üzere gönderildi.')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class MakalelerimView(LoginRequiredMixin, ListView):
    model = Makale
    template_name = 'articles/makalelerim.html'
    context_object_name = 'makaleler'

    def get_queryset(self):
        # Giriş yapan kullanıcının Yazar profili varsa, ona ait makaleleri getir
        user = self.request.user
        try:
            yazar = user.yazar_profili
            return Makale.objects.filter(yazarlar=yazar).select_related(
                'dergi_sayisi'
            ).prefetch_related('yazarlar', 'yazarlar__user_hesabi')
        except Exception:
            return Makale.objects.select_related('dergi_sayisi').prefetch_related('yazarlar')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['toplam_makale'] = queryset.count()
        context['yayindaki_makale'] = queryset.filter(goster_makaleler_sayfasinda=True).count()
        context['taslak_makale'] = queryset.filter(goster_makaleler_sayfasinda=False).count()
        return context

# YENİ VIEW: Makale Güncelleme
class MakaleUpdateView(AuthorRequiredMixin, UpdateView):
    model = Makale
    form_class = MakaleForm # Normal kullanıcılar bu formu kullanır
    template_name = 'articles/makale_form.html'
    
    def get_success_url(self):
        return reverse_lazy('makale_detail', kwargs={'slug': self.object.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Makale Düzenle'
        context['submit_text'] = 'Kaydet'
        # Admin notu şablonda göstermek için context'e ekle
        if self.object.admin_notu:
            context['admin_notu'] = self.object.admin_notu
        return context
    
    def form_valid(self, form):
        """
        Form kaydedilirken yeni iş akışını uygular:
        1. Yazar notu okuduysa, 'admin_notu_okundu' olarak işaretlenir.
        2. Makale yayındaysa, düzenleme sonrası taslağa çekilir.
        """
        makale = form.instance
        # 1. Bildirim sayısını düşürme mantığı
        if not self.object.admin_notu_okundu and self.object.admin_notu:
             makale.admin_notu_okundu = True
             messages.info(self.request, "Editör notunu okuduğunuz için bildiriminiz kaldırıldı.")
        # 2. Yayındaki makaleyi taslağa çekme mantığı
        if self.object.goster_makaleler_sayfasinda and not self.request.user.is_superuser:
            makale.goster_makaleler_sayfasinda = False
            messages.warning(self.request, "Yayındaki makalenizde değişiklik yaptığınız için makaleniz yeniden incelenmek üzere taslaklara taşındı.")
        form.save()
        return redirect(self.get_success_url())

# YENİ VIEW: Makale Silme
class MakaleDeleteView(AuthorRequiredMixin, DeleteView):
    model = Makale
    template_name = 'articles/makale_confirm_delete.html'
    success_url = reverse_lazy('makalelerim')

    def form_valid(self, form):
        # success_message'i obj silinmeden önce al
        success_message = f"'{self.object.baslik}' başlıklı makale başarıyla silindi."
        self.object.delete()
        messages.success(self.request, success_message)
        return redirect(self.success_url)

@login_required
@require_POST
def check_author_view(request):
    """
    AJAX isteği ile gönderilen yazar metnini kontrol eder.
    Sadece @kullaniciadi ile veya sadece isim ile çalışır.
    """
    author_text = request.POST.get('author_text', '').strip()
    if not author_text:
        return JsonResponse({'status': 'error', 'message': 'Yazar adı boş olamaz.'}, status=400)

    # Senaryo 1: Kayıtlı kullanıcıyı kontrol et (@kullaniciadi)
    # Metnin başında ve sonunda boşluk olmadan sadece @ ile başlayıp başlamadığını kontrol et
    if author_text.startswith('@'):
        username = author_text[1:] # @ işaretini kaldır
        try:
            user = User.objects.get(username=username)
            # Kullanıcının tam ismini profilden alıyoruz
            isim_soyisim = user.get_full_name()
            if not isim_soyisim: # Eğer kullanıcı isim girmemişse, kullanıcı adını kullan
                isim_soyisim = user.username

            return JsonResponse({
                'status': 'success',
                'isim_soyisim': isim_soyisim, # Otomatik olarak bulunan isim
                'username': user.username,
                'is_registered': True
            })
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': f"'{username}' kullanıcı adı ile kayıtlı bir yazar bulunamadı."}, status=404)
            
    # Senaryo 2: Harici yazar (sadece isim soyisim)
    else:
        # @ işareti içeriyorsa, formatın yanlış olduğunu belirt
        if '@' in author_text:
            return JsonResponse({'status': 'error', 'message': "Kayıtlı kullanıcı eklemek için sadece '@kullaniciadi' formatını kullanın."}, status=400)

        return JsonResponse({
            'status': 'success',
            'isim_soyisim': author_text,
            'username': None,
            'is_registered': False
        })

@login_required
@require_POST
def update_article_order(request):
    """
    Makalelerin ve içeriklerin sıralamasını günceller. Sadece admin kullanıcıları kullanabilir.
    """
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Bu işlem için admin yetkisi gereklidir.'}, status=403)
    
    try:
        data = json.loads(request.body)
        dergi_sayisi_id = data.get('dergi_sayisi_id')
        article_orders = data.get('article_orders', [])
        content_orders = data.get('content_orders', [])
        
        if not dergi_sayisi_id:
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
        
        # İçeriklerin sıralamasını güncelle
        for order_data in content_orders:
            content_id = order_data.get('id')
            new_order = order_data.get('order')
            
            if content_id is not None and new_order is not None:
                try:
                    from .models import DergiIcerigi
                    content = DergiIcerigi.objects.get(id=content_id, dergi_sayisi=dergi_sayisi)
                    content.siralama = new_order
                    content.save(update_fields=['siralama'])
                except DergiIcerigi.DoesNotExist:
                    continue  # İçerik bulunamadı, devam et
        
        return JsonResponse({'status': 'success', 'message': 'Sıralama başarıyla güncellendi.'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON verisi.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Bir hata oluştu: {str(e)}'}, status=500)

@login_required
def get_articles_for_ordering(request, dergi_sayisi_id):
    """
    Belirli bir dergi sayısındaki makaleleri sıralama için getirir.
    """
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Bu işlem için admin yetkisi gereklidir.'}, status=403)
    
    try:
        dergi_sayisi = DergiSayisi.objects.get(id=dergi_sayisi_id)
        makaleler = Makale.objects.filter(dergi_sayisi=dergi_sayisi).order_by('siralama', '-olusturulma_tarihi')
        
        articles_data = []
        for makale in makaleler:
            articles_data.append({
                'id': makale.id,
                'baslik': makale.baslik,
                'yazarlar': makale.get_yazarlar_display(),
                'siralama': makale.siralama,
                'yayinda_mi': makale.goster_makaleler_sayfasinda,
                'olusturulma_tarihi': makale.olusturulma_tarihi.strftime('%d.%m.%Y %H:%M')
            })
        
        return JsonResponse({
            'status': 'success',
            'dergi_sayisi': {
                'id': dergi_sayisi.id,
                'tarih': dergi_sayisi.get_tarih_format(),
                'cilt_sayi': dergi_sayisi.get_cilt_sayi_format()
            },
            'makaleler': articles_data
        })
        
    except DergiSayisi.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Dergi sayısı bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Bir hata oluştu: {str(e)}'}, status=500)