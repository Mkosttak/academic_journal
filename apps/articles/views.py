from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Makale, DergiSayisi
from .forms import MakaleForm
from apps.core.mixins import AdminRequiredMixin, AuthorRequiredMixin

# Create your views here.

class MakaleListView(ListView):
    model = Makale
    template_name = 'articles/makale_list.html'
    context_object_name = 'makaleler'
    paginate_by = 10

    def get_queryset(self):
        # Sadece yayında olan makaleleri göster
        queryset = Makale.objects.filter(goster_makaleler_sayfasinda=True)
        
        # Filtreleme ve Arama
        dergi_no = self.request.GET.get('dergi')
        query = self.request.GET.get('q')

        if dergi_no:
            queryset = queryset.filter(dergi_sayisi__id=dergi_no)
        if query:
            queryset = queryset.filter(
                Q(baslik__icontains=query) |
                Q(yazarlar__first_name__icontains=query) |
                Q(yazarlar__last_name__icontains=query) |
                Q(anahtar_kelimeler__icontains=query)
            ).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dergi_sayilari'] = DergiSayisi.objects.all()
        return context

class MakaleDetailView(DetailView):
    model = Makale
    template_name = 'articles/makale_detail.html'
    context_object_name = 'makale'

    def get_object(self, queryset=None):
        # Slug ile makaleyi bul
        obj = super().get_object(queryset=queryset)
        # Görüntülenme sayısını artır
        obj.goruntulenme_sayisi += 1
        obj.save(update_fields=['goruntulenme_sayisi'])
        return obj

class MakaleCreateView(LoginRequiredMixin, CreateView):
    model = Makale
    form_class = MakaleForm
    template_name = 'articles/makale_form.html'
    success_url = reverse_lazy('makalelerim') # Makale eklendikten sonra 'Makalelerim' sayfasına yönlendir

    def get_form_kwargs(self):
        kwargs = super(MakaleCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        # Formu kaydederken, formu gönderen kullanıcıyı yazar olarak ata
        form.instance.save() # Önce makaleyi kaydet
        form.instance.yazarlar.add(self.request.user) # Sonra yazarı ekle
        return super().form_valid(form)

class MakalelerimView(LoginRequiredMixin, ListView):
    model = Makale
    template_name = 'articles/makalelerim.html'
    context_object_name = 'makaleler'

    def get_queryset(self):
        # Sadece giriş yapmış kullanıcının yazdığı makaleleri listele
        return Makale.objects.filter(yazarlar=self.request.user)
    
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
        context['page_title'] = 'Makale Düzenle'
        # Admin notu şablonda göstermek için context'e ekle
        if self.object.admin_notu:
            context['admin_notu'] = self.object.admin_notu
        return context
    
    def form_valid(self, form):
        # Makale güncellendiğinde, admin notu okunmuş sayılabilir.
        # Bu mantığı daha da geliştirebiliriz. Şimdilik admin notu okunmuşsa,
        # kullanıcı düzenleme yaptığında tekrar okunmadı yapmayalım.
        makale = form.save(commit=False)
        if self.request.user in makale.yazarlar.all() and not makale.admin_notu_okundu:
            makale.admin_notu_okundu = True
        makale.save()
        form.save_m2m()
        return super().form_valid(form)

# YENİ VIEW: Makale Silme
class MakaleDeleteView(AuthorRequiredMixin, DeleteView):
    model = Makale
    template_name = 'articles/makale_confirm_delete.html'
    success_url = reverse_lazy('makalelerim')
