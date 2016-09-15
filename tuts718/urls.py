from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from registration.backends.simple.views import RegistrationView

class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return '/'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tuts718.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('TuTz718.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


