from django.conf import settings

def notification_context(request):
    """
    Navbar bildirim sayısı için context processor
    """
    context = {}
    
    if request.user.is_authenticated:
        # Admin notu sayısı
        if hasattr(request.user, 'yazar_profili'):
            try:
                from articles.models import Makale
                unread_notes = Makale.objects.filter(
                    yazarlar=request.user.yazar_profili,
                    admin_notu_okundu=False,
                    admin_notu__isnull=False
                ).count()
                context['unread_admin_notes'] = unread_notes
            except:
                context['unread_admin_notes'] = 0
        else:
            context['unread_admin_notes'] = 0
        
        # Cevap bekleyen mesaj sayısı (sadece admin için)
        if request.user.is_superuser:
            try:
                from pages.models import IletisimFormu
                unread_messages = IletisimFormu.objects.filter(cevaplandi=False).count()
                context['unread_messages'] = unread_messages
            except:
                context['unread_messages'] = 0
        else:
            context['unread_messages'] = 0
    
    return context

def site_settings(request):
    """
    Site genel ayarları için context processor
    """
    return {
        'SITE_NAME': 'Akademik Dergi',
        'SITE_DESCRIPTION': 'Akademik araştırma ve makale yayınlama platformu',
        'SITE_URL': request.build_absolute_uri('/'),
    }