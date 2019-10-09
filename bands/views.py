from django.views.generic import CreateView, ListView, DetailView
from .forms import CreateBandForm
from .models import Band
from accounts.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from accounts.mixins import VerifiedUserMixin
from django.http import JsonResponse


class CreateBandView(VerifiedUserMixin, CreateView):
    template_name = 'create_form.html'
    form_class = CreateBandForm
    success_url = reverse_lazy('create_band')

    def form_valid(self, form):
        band = form.save(commit=False)
        band.user = User.create_placeholder_user(band.name)
        messages.success(self.request, '%s has been added successfully' % band.name)
        return super(CreateBandView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateBandView, self).get_context_data(**kwargs)
        context['title'] = "Create Band"
        return context


class BandListView(ListView):
    template_name = 'band_list.html'
    context_object_name = 'band_list'
    model = Band
    paginate_by = 12


class BandDetailView(DetailView):
    template_name = 'band_details.html'
    context_object_name = 'band'
    model = Band


def band_json(request):
    bands_list = {'items': [{'text': band.name, 'id': band.pk} for band in Band.objects.filter(name__icontains=request.GET['q'])]}
    return JsonResponse(bands_list)
