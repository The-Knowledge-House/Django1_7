from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from models import Category, Page, UserProfile
from forms import CategoryForm, PageForm, UserForm, UserProfileForm, ContactForm, PasswordRecoveryForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from bing_search import run_query
from django.contrib.auth.models import User
from suggest import get_category_list
from django.views.generic import FormView
from django.contrib.auth.forms import PasswordChangeForm
from braces.views import LoginRequiredMixin


# Create your views here.

def index(request):
	#request.session.set_test_cookie()


	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories' : category_list,
					'pages' : page_list
					}
	# If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
	#visits =  int(request.COOKIES.get('visits', 1))
	visits = request.session.get('visits')

	if not visits:
		visits = 1

	reset_last_visit_time = False

	#response = render(request, 'index.html', context_dict)
	# Does the cookie last_visit exist?
	last_visit = request.session.get('last_visit')
	if last_visit:
		# Yes it does Get the cookie's value.
		#last_visit = request.COOKIES['last_visit']
		#Cast the value to a Python date/time object.
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		# If it's been more than a day since the last visit increase by 1
		if (datetime.now() - last_visit_time).days > 0:
			visits = visits + 1
			#flag cookie to be updated.
			reset_last_visit_time = True 
	else:
		#Cookie last_visit doesn't exist, so flag that it should be set.
		reset_last_visit_time = True
		#context_dict['visits'] = visits
		#Obtain our Response object early so we can add cookie information.
		#response = render(request, 'index.html', context_dict)

	if reset_last_visit_time:
		#response.set_cookie('last_visit', datetime.now())
		request.session['last_visit'] = str(datetime.now())
		#response.set_cookie('visits', visits)
		request.session[visits] = visits
	context_dict['visits'] = visits

	return render(request, 'index.html', context_dict)



def about(request):
	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 1
	return render(request, 'about.html', {'visits':count})

@login_required
def category(request, category_name_slug):
	context_dict = {}
	context_dict['query'] = None
	context_dict['result_list'] = None

	if request.method == 'POST':
			query = request.POST['query'].strip()
			if query:
				result_list = run_query(query)
				context_dict['result_list'] =  result_list
				context_dict['query'] = query

	try:
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
		pages = Page.objects.filter(category=category).order_by('-views')
		context_dict['pages'] = pages
		context_dict['category'] = category

	except Category.DoesNotExist:
		pass

	if not context_dict['query']:
		context_dict['query'] =  category.name 


	return render(request, 'category.html', context_dict)

@login_required
def user_profile(request, user_username):
	context_dict = {}
	user = User.objects.get(username=user_username)
	profile = UserProfile.objects.get(user=user)
	context_dict['profile'] = profile

	return render(request, 'profile.html', context_dict) 


@login_required
def edit_profile(request, user_username):
	profile = get_object_or_404(UserProfile, user__username=user_username)
	website = profile.website
	pic = profile.pic

	if request.user != profile.user: 
		return HttpResponse('Access Denied')

	if request.method == 'POST':
		#form = UserProfileForm(request.POST or None,  
		#					request.FILES or None, 
		#					instance=profile)
		if form.is_valid():
		#	form.save()
					
		#	return user_profile(request, profile.user.username)

			if 'website' in request.POST:
				profile.website = request.POST['website']
			else:
				profile.website = website

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			else:
				profile.picture = pic

			profile.save()

			return user_profile(request, profile.user.username)

		else:
			print form.errors

	else:
		form = UserProfileForm()

	return render(request, 
				'edit_profile.html', 
				{'form':form, 'profile': profile})









@login_required
def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()

	return render(request, 'add_category.html', {'form':form})


@login_required
def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug=category_name_slug)

	except Category.DoesNotExist:
			cat = None

	if request.method == 'POST':
		form =  PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				return category(request, category_name_slug)
			else:
				print form.errors
		else:
			print form.errors
	else:
		form = PageForm()
	context_dict = {'form':form, 'category': cat, 'slug': category_name_slug}

	return render(request, 'add_page.html', context_dict)

def register(request):
	#init bool to f change to t on success
	registered = False
	#if request.session.test_cookie_worked():
	#	print '>>>Test Cookie Worked'
	#	request.session.delete_test_cookie()
	if request.method == 'POST':
		user_form =  UserForm(data=request.POST)
		profile_form =  UserProfileForm(data=request.POST)


		if user_form.is_valid() and profile_form.is_valid():

			user = user_form.save()
			#save data
			user.set_password(user.password)
			#hash pw in db
			user.save()
			#resave

			profile = profile_form.save(commit=False)

			profile.user = user 

			if 'picture' in request.FILES: #if pic add pic to user profile

				profile.picture = request.FILES['picture']

			profile.save()

			registered = True #success

		else:
			print user_form.errors, profile_form.errors

	else:

		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'register.html', 
					{'user_form': user_form, 
					'profile_form':profile_form, 
					'registered':registered}
					)



def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user =  authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/')
			else:
				return HttpResponse('You account has been deactivated.')

		else:
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")

	else:
		return render(request, 'login.html', {})

def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')


#@login_required
#def restricted(request):
#	return HttpResponse("Since you're logged in, you can see this text!")


def track_url(request):
	page_id = None
	url = '/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				url = page.url
			except: 
				pass
	print 'forward', page.views
	return redirect(url)



def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)

		if form.is_valid():
			form.send_message()

			return HttpResponseRedirect('/')
		else:
			print form.errors

	form = ContactForm()
	return render('contact.html', {'form':form})



@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
	likes = 0
	if cat_id:
		cat = Category.objects.get(id=int(cat_id))
		if cat:
			likes = cat.likes + 1
			cat.likes = likes
			cat.save()
	return HttpResponse(likes)


def suggest_category(request):
	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with =  request.GET['suggestion']
	cat_list = get_category_list(8, starts_with)

	return render(request, 'rango/cats.html', {'cat_list': cat_list })


@login_required
def auto_page_add(request):
	cat_id = None
	url = None
	title = None
	context_dict = {}

	if request.method == 'GET':
		cat_id =  request.GET['categry_id']
		url =  request.GET['url']
		title = request.GET['title']

		if cat_id:
			category = Category.objects.get(id=int(cat_id))
			p = Page.objects.get_or_create(category=category, title=title, url=url)

			pages = Page.objects.filter(category=category).order_by('-views')

			context_dict['pages'] = pages

	return render(request, 'rango/page_list.html', context_dict)


#def some_view(request):
 #   if not request.user.is_authenticated():
   #     return HttpResponse("You are logged in.")
  #  else:
    #    return HttpResponse("You are not logged in.")

class PasswordRecoveryView(FormView):
	template_name = 'password_recovery.html'
	form_class = PasswordRecoveryForm
	success_url = reverse_lazy('login')
	def form_valid(self, form):
		form.reset_email()
		return super(PasswordRecoveryView, self).form_valid(form)


class SettingsView(LoginRequiredMixin, FormView):
	template_name = 'settings.html'
	form_class = PasswordChangeForm
	success_url = reverse_lazy('dashboard')
	login_url = '/login/'
