from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json

def generate_meta_tags(title, description, keywords="", author="", image_url="", article_type="website"):
    """
    SEO meta etiketlerini oluşturur
    """
    meta_tags = {
        'title': title,
        'description': description,
        'keywords': keywords,
        'author': author,
        'og_title': title,
        'og_description': description,
        'og_image': image_url,
        'og_type': article_type,
        'twitter_card': 'summary_large_image',
        'twitter_title': title,
        'twitter_description': description,
        'twitter_image': image_url,
    }
    return meta_tags

def generate_breadcrumb(items):
    """
    Breadcrumb JSON-LD oluşturur
    """
    breadcrumb_data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for i, item in enumerate(items):
        breadcrumb_data["itemListElement"].append({
            "@type": "ListItem",
            "position": i + 1,
            "name": item['name'],
            "item": item.get('url', '')
        })
    
    return json.dumps(breadcrumb_data, ensure_ascii=False)

def generate_article_schema(article):
    """
    Makale için Schema.org JSON-LD oluşturur
    """
    schema_data = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": article.baslik,
        "description": article.aciklama,
        "author": [],
        "publisher": {
            "@type": "Organization",
            "name": "Akademik Dergi",
            "url": "https://yourdomain.com"
        },
        "datePublished": article.olusturulma_tarihi.isoformat(),
        "dateModified": article.guncellenme_tarihi.isoformat(),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://yourdomain.com/makaleler/detay/{article.slug}/"
        }
    }
    
    # Yazarları ekle
    for yazar in article.yazarlar.all():
        schema_data["author"].append({
            "@type": "Person",
            "name": yazar.isim_soyisim
        })
    
    # Dergi bilgisi varsa ekle
    if article.dergi_sayisi:
        schema_data["isPartOf"] = {
            "@type": "PublicationIssue",
            "issueNumber": article.dergi_sayisi.sayi_no,
            "datePublished": f"{article.dergi_sayisi.yil}-{article.dergi_sayisi.ay:02d}-01"
        }
    
    return json.dumps(schema_data, ensure_ascii=False)

def generate_organization_schema():
    """
    Organizasyon için Schema.org JSON-LD oluşturur
    """
    schema_data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Akademik Dergi",
        "url": "https://yourdomain.com",
        "logo": "https://yourdomain.com/static/images/logo.png",
        "description": "Akademik araştırma ve makale yayınlama platformu",
        "sameAs": [
            "https://twitter.com/yourjournal",
            "https://linkedin.com/company/yourjournal"
        ]
    }
    
    return json.dumps(schema_data, ensure_ascii=False)

def generate_sitemap_urls():
    """
    Sitemap için URL listesi oluşturur
    """
    from articles.models import Makale, DergiSayisi
    from pages.models import IletisimFormu
    
    urls = [
        {
            'loc': '/',
            'changefreq': 'daily',
            'priority': '1.0'
        },
        {
            'loc': '/sayilar/',
            'changefreq': 'weekly',
            'priority': '0.8'
        },
        {
            'loc': '/editorler/',
            'changefreq': 'monthly',
            'priority': '0.6'
        },
        {
            'loc': '/iletisim/',
            'changefreq': 'monthly',
            'priority': '0.5'
        }
    ]
    
    # Makaleleri ekle
    for makale in Makale.objects.filter(goster_makaleler_sayfasinda=True):
        urls.append({
            'loc': f'/makaleler/detay/{makale.slug}/',
            'changefreq': 'monthly',
            'priority': '0.7',
            'lastmod': makale.guncellenme_tarihi
        })
    
    # Dergi sayılarını ekle
    for dergi in DergiSayisi.objects.filter(yayinlandi_mi=True):
        urls.append({
            'loc': f'/sayilar/{dergi.slug}/',
            'changefreq': 'monthly',
            'priority': '0.6',
            'lastmod': dergi.olusturulma_tarihi
        })
    
    return urls
