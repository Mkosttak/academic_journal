from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView
from django.urls import reverse_lazy
from .forms import IletisimModelForm
from users.models import User
from django.contrib import messages

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
