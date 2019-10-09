class RegionMixin(object):
    def get_queryset(self):
        queryset = super(RegionMixin, self).get_queryset()
        return queryset.filter(region=self.request.region)


class RegionCreateViewMixin(object):
    def form_valid(self, form):
        form.instance.region = self.request.region
        return super(RegionCreateViewMixin, self).form_valid(form)
