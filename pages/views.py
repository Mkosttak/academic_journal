from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from .forms import IletisimModelForm
from users.models import User
from articles.models import DergiSayisi, Makale, DergiIcerigi
from django.contrib import messages
from collections import defaultdict
from datetime import datetime

# Create your views here.

class AnasayfaView(TemplateView):
    template_name = 'pages/anasayfa.html'

class IletisimView(CreateView):
    form_class = IletisimModelForm
    template_name = 'pages/iletisim.html'
    success_url = reverse_lazy('anasayfa') # Mesaj gönderildikten sonra anasayfaya yönlendir

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Mesajınız başarıyla gönderildi. En kısa sürede size geri döneceğiz.')
        return response

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class EditorlerListView(ListView):
    model = User
    template_name = 'pages/editorler.html'
    context_object_name = 'editorler'
    paginate_by = 12 # Sayfa başına 12 editör göster

    def get_queryset(self):
        # Sadece editör yetkisi olan ve Editörler sayfasında görünmesi istenen kullanıcıları listele
        return User.objects.filter(is_editor=True, goster_editorler_sayfasinda=True)


class SayilarListView(ListView):
    model = DergiSayisi
    template_name = 'pages/sayilar.html'
    context_object_name = 'dergi_sayilari'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Seçili yılı al (URL parametresinden)
        secili_yil = self.request.GET.get('yil')
        
        # Dergi sayılarını yıl ve ay'a göre sırala (sadece yayınlanmış olanlar)
        dergi_sayilari = DergiSayisi.objects.filter(
            yayinlandi_mi=True
        ).annotate(
            yayindaki_makale_sayisi=Count('makaleler', filter=Q(makaleler__goster_makaleler_sayfasinda=True))
        ).order_by('-yil', '-ay', '-sayi_no')
        
        # Yıllara göre gruplama (sidebar için)
        yillar = defaultdict(list)
        for dergi in dergi_sayilari:
            yillar[dergi.yil].append(dergi)
        
        # Sırala (en yeni yıl önce)
        yillar_sirali = dict(sorted(yillar.items(), reverse=True))
        context['yillar'] = yillar_sirali
        
        # Eğer yıl seçilmişse, sadece o yılın dergilerini göster
        if secili_yil:
            try:
                secili_yil = int(secili_yil)
                dergi_sayilari = dergi_sayilari.filter(yil=secili_yil)
                context['secili_yil'] = secili_yil
            except (ValueError, TypeError):
                pass
        
        context['tum_dergiler'] = dergi_sayilari
        
        return context


class SayiMakaleleriView(ListView):
    model = Makale
    template_name = 'pages/sayi_makaleleri.html'
    context_object_name = 'makaleler'
    paginate_by = 20
    
    def get_queryset(self):
        self.dergi_sayisi = get_object_or_404(DergiSayisi, pk=self.kwargs['sayi_id'])
        return Makale.objects.filter(
            dergi_sayisi=self.dergi_sayisi,
            goster_makaleler_sayfasinda=True
        ).select_related('dergi_sayisi').prefetch_related('yazarlar').order_by('-olusturulma_tarihi')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dergi_sayisi'] = self.dergi_sayisi
        
        # Yayında olan dergi içeriklerini de ekle (makalelerden sonra göstermek için)
        context['dergi_icerikleri'] = DergiIcerigi.objects.filter(
            dergi_sayisi=self.dergi_sayisi,
            yayinda_mi=True
        ).order_by('-olusturulma_tarihi')
        
        return context
