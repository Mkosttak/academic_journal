# core/context_processors.py

from articles.models import Makale
from pages.models import IletisimFormu

def notification_context(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user
    context = {}

    # Admin için okunmamış iletişim formu mesajları
    if user.is_superuser:
        context['unread_messages_count'] = IletisimFormu.objects.filter(cevaplandi=False).count()
    else:
        context['unread_messages_count'] = 0

    # Admin ve Editör için taslak makaleler
    if user.is_superuser or user.is_editor:
        context['draft_articles_count'] = Makale.objects.filter(goster_makaleler_sayfasinda=False).count()
    else:
        context['draft_articles_count'] = 0
        
    # Her kullanıcı için sadece kendi makalelerinde yeni admin notu varsa say
    context['unread_notes_count'] = Makale.objects.filter(
        yazarlar__user_hesabi=user,
        admin_notu_okundu=False
    ).exclude(admin_notu__isnull=True).exclude(admin_notu__exact='').count()

    return context