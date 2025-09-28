# core/storage.py
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import setting

class StaticStorage(S3Boto3Storage):
    """Static dosyalar için S3 storage"""
    bucket_name = setting('AWS_STORAGE_BUCKET_NAME')
    custom_domain = setting('AWS_S3_CUSTOM_DOMAIN')
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True
    
    def __init__(self, *args, **kwargs):
        kwargs['querystring_auth'] = False
        super().__init__(*args, **kwargs)

class MediaStorage(S3Boto3Storage):
    """Media dosyalar için S3 storage"""
    bucket_name = setting('AWS_STORAGE_BUCKET_NAME')
    custom_domain = setting('AWS_S3_CUSTOM_DOMAIN')
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    
    def __init__(self, *args, **kwargs):
        kwargs['querystring_auth'] = False
        super().__init__(*args, **kwargs)

class OptimizedImageStorage(S3Boto3Storage):
    """Optimize edilmiş resimler için S3 storage"""
    bucket_name = setting('AWS_STORAGE_BUCKET_NAME')
    custom_domain = setting('AWS_S3_CUSTOM_DOMAIN')
    location = 'optimized'
    default_acl = 'public-read'
    file_overwrite = True
    
    def __init__(self, *args, **kwargs):
        kwargs['querystring_auth'] = False
        super().__init__(*args, **kwargs)
