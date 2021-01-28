from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    @classmethod
    def as_view(self, *args, **kwargs):
        view = super().as_view()
        return login_required(view)