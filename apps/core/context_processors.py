from apps.articles.models import Makale
from apps.pages.models import IletisimFormu

def notification_context(request):
    if not request.user.is_authenticated:
        return {}

    context = {
        'unread_messages_count': 0,
        'draft_articles_count': 0,
        'unread_notes_count': 0,
    }

    user = request.user

    # Admin için okunmamış iletişim formu mesajları
    if user.is_superuser:
        context['unread_messages_count'] = IletisimFormu.objects.filter(cevaplandi=False).count()

    # Admin ve Editör için taslak makaleler
    if user.is_superuser or user.is_editor:
        context['draft_articles_count'] = Makale.objects.filter(goster_makaleler_sayfasinda=False).count()
        
    # Tüm giriş yapmış kullanıcılar için okunmamış admin notları
    # Sadece kullanıcının yazar olduğu ve notu okunmamış makaleleri say
    context['unread_notes_count'] = Makale.objects.filter(
        yazarlar=user, 
        admin_notu_okundu=False
    ).exclude(admin_notu__isnull=True).exclude(admin_notu__exact='').count()

    return context 