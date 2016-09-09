from django.conf.urls import patterns, url 
from TuTz718 import views


urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name="about"),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
	url(r'^user/(?P<user_username>[\w\-]+)/$', views.user_profile, name='profile'),
	url(r'^user/edit/(?P<user_username>[\w\-]+)/$', views.edit_profile, name='edit_profile'),
	url(r'^add_category/$', views.add_category, name='add_category'),
	url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/', views.add_page, name='add_page'),
	url(r'^register/$', views.register, name='register'),
	url(r'^login/$', views.user_login, name='login'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^goto/$', views.track_url, name='goto'),
	#url(r'^restricted/$', views.about, name="restricted"),
	)



