from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from models import Category, Page
from forms import CategoryForm, PageForm, UserForm, UserProfileForm
# Create your views here.

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories' : category_list,
					'pages' : page_list
					}
	return render(request, 'index.html', context_dict)
	

def about(requrest):
	return HttpResponse("About")

def category(request, category_name_slug):
	context_dict = {}

	try:
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name

		pages = Page.objects.filter(category=category)

		context_dict['pages'] = pages

		context_dict['category'] = category

		context_dict['slug'] = category_name_slug

	except Category.DoesNotExist:
		pass

	return render(request, 'category.html', context_dict)

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







