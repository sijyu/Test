# Create your views here.
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, get_user_model
#from loginPortal.models import Volunteer, Log , RegiForm, MedicalInformtaion,VolunteerManager
from loginPortal.models import User, Log , RegiForm, MedicalInformtaion,UserManager
from django.views.generic.edit import CreateView
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required 
#requires authentication before accessing page. denoted
# by: @login_required
import datetime

user = get_user_model()

# this is a tiny dictionary that holds all of the work types
work_types = dict()
work_types['Administration'] = 'a'
work_types['Staff'] = 'n'
work_types['Volunteer'] = 'm'
work_types['Other'] = 'o'

# this will help us figure out the total quarterly hours on the views
global_now = timezone.now()
global_year = global_now.year
date_list = ( 
	datetime.date(global_year, 1, 1), 
	datetime.date(global_year, 4, 1), 
	datetime.date(global_year, 7, 1), 
	datetime.date(global_year, 10, 1)
)

# this is a buffer view that will eventually become the authentication portal
def my_login(request):
	# just go to this page - it will go to an authentications view when pressed enter
	return render(request, 'loginPortal/login.html', {})


#this is a registration form
@login_required(login_url='/login/')
def regi(request):
	if request.method == 'POST':
		form = RegiForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			address = form.cleaned_data['address']
			phone_number = form.cleaned_data['phone_number']
			password = form.cleaned_data['password']
			User.objects.create_user(email, first_name, last_name, address, phone_number, password)
  
			return HttpResponse('<script language="JavaScript"> alert("Thanks for register!"); location.href="http://127.0.0.1:8000/login/regi/"</script>')
	else:
         form = RegiForm()
	return render(request, 'loginPortal/regiform.html',{'form' : form})


#this is a medical form
@login_required(login_url='/login/')
def medical(request):
    if request.method == 'POST':
        form = MedicalInformtaion(request.POST)
        if form.is_valid():
            volunteer_health_notes = form.cleaned_data['volunteer_health_notes']
            volunteer_medications = form.cleaned_data['volunteer_medications']
            volunteer_allergies = form.cleaned_data['volunteer_allergies']
            User.objects.create_user(volunteer_allergies, volunteer_medications, volunteer_health_notes)
            
            return HttpResponse('<script language="JavaScript"> alert("Thanks for your medical information!"); location.href="http://127.0.0.1:8000/login/medical/"</script>')  
    else:
         form = MedicalInformtaion()
    return render(request, 'loginPortal/medical.html',{'form' : form})






	
# this is our authentication buffer, it takes the post from the login page and then just goes to work
def auth_buff(request):
	email = request.POST['email']
	password = request.POST['password']
	volunteer = authenticate(email=email, password=password)
	
	if volunteer:
		#return HttpResponseRedirect('/login/loged/')
		if volunteer.is_active:
			login(request, volunteer)

			# we probably don't need this, but just in case
			vol_bool = volunteer.is_staff
			
			# if they haven't clocked out and are staff
			if Log.objects.filter(volunteer__email = volunteer.email, clock_out = None) and vol_bool:
				return HttpResponseRedirect('/login/clock_out')
			
			#staff looking to clock in
			elif vol_bool:
			
				return HttpResponseRedirect('/login/clock_in')
			
			# time stamp
			else:
				return HttpResponseRedirect('/login/volunteer_detail')
		
		else:
			return HttpResponse('<script language="JavaScript"> alert("You are not active yet!"); location.href="http://127.0.0.1:8000/login/"</script>')
	else:
		return HttpResponse('<script language="JavaScript"> alert("Bad email and/or password"); location.href="http://127.0.0.1:8000/login/"</script>')

#Temporary loged page
@login_required(login_url='/login/')
def loged(request):
	volunteer = request.user
	user_name = volunteer.first_name
	user_email = volunteer.email

	return render(request, 'loginPortal/loged.html', {'user_name' : user_name, 'use_remail' : user_email})

# this is the view that holds the business logic for the clock in and out system
@login_required(login_url='/login/')
def clock_in(request):
	volunteer = request.user
	user = volunteer.email
	# snag all of the times when this volunteer logged in
	overall_hours_raw = Log.objects.filter(volunteer__email = volunteer.email).aggregate(Sum('total_hours'))
	overall_hours = overall_hours_raw['total_hours__sum']
	if overall_hours:
		overall_hours = int(overall_hours)
	else:
		overall_hours = 0

	vol_bool = volunteer.is_staff
	
	if vol_bool:
		return render(request, 'loginPortal/clock_in.html', {'user' : user, 'overall_hours' : overall_hours})
	else:
		return render(request, 'loginPortal/volunteer/clock_in.html', {'user' : user, 'overall_hours' : overall_hours})

@login_required(login_url='/login/')	
def log_buff(request):
	volunteer = request.user
	clock_in = timezone.now()
	work_type = 'a'	
	#if request.method == 'POST':
	L = volunteer.log_set.create(clock_in = clock_in, work_type = work_type)
	L.save()
	return HttpResponseRedirect('/login/clock_out')


@login_required(login_url='/login/')	
def clock_out(request):
	# should just load that clock-out page, when you hit clock-in
	volunteer = request.user
	user = volunteer.email
	# snag all of the times when this volunteer logged in
	overall_hours_raw = Log.objects.filter(volunteer__email = volunteer.email).aggregate(Sum('total_hours'))
	overall_hours = overall_hours_raw['total_hours__sum']
	if overall_hours:
		overall_hours = int(overall_hours)
	else:
		overall_hours = 0

	vol_bool = volunteer.is_staff
	
	if vol_bool:
		return render(request, 'loginPortal/clock_out.html', {'user' : user, 'overall_hours' : overall_hours})
	else:
		return render(request, 'loginPortal/volunteer/clock_out.html', {'user' : user, 'overall_hours' : overall_hours})

@login_required(login_url='/login/')	
def out_buff(request):
	volunteer = request.user
	# now we will do some fancy conversion to change days and seconds into hours
	now = timezone.now()
	L = Log.objects.get(volunteer__email = volunteer.email, clock_out = None)
	L.clock_out = now
	diff = now - L.clock_in
	hours = diff.days * 24 + float(diff.seconds) / 3600
	L.total_hours = hours
	
	# save that stuff
	L.save()
	return HttpResponseRedirect('/login/clock_in')

# here are the functions that will deal with the time stamp 
@login_required(login_url='/login/')
def time_stamp(request):
	volunteer = request.user
	user = volunteer.email
	welcome = "Hello %s, you are at the time stamp portal" % volunteer.email

	vol_bool = volunteer.is_staff

	if vol_bool:
		return render(request, 'loginPortal/time_stamp.html', {'user' : user})
	else:
		return render(request, 'loginPortal/volunteer/time_stamp.html', {'user' : user})
	
# this is a tiny dictionary that holds all of the work types
@login_required(login_url='/login/')
def time_stamp_buff(request):
	volunteer = request.user
	work_type = request.POST['work_type']
	total_hours = request.POST['total_hours']
	date = request.POST['date']
	new_time = volunteer.log_set.create(clock_in = date, clock_out = date, total_hours = total_hours, work_type = work_types[work_type])
	new_time.save()
	return HttpResponseRedirect('/login/time_stamp')


@login_required(login_url='/login/')	
def missedpunch(request):
	# loads missedpunch page
	return render(request, 'loginPortal/missedpunch.html', {})
	
@login_required
def my_logout(request):
	logout(request)
	return HttpResponseRedirect('/login/')

@login_required(login_url='/login/')
def volunteer(request):

	query_results = User.objects.all()

	return render(request, 'loginPortal/volunteer.html', {'query_results' : query_results})

@login_required(login_url='/login/')
def detail(request):
	detail_id = request.GET['id']
	query_results = User.objects.filter(id = detail_id)

	return render(request, 'loginPortal/detail.html', {'query_results': query_results})

@login_required(login_url='/login/')
def volunteer_detail(request):
	volunteer = request.user
	user = volunteer.id
	query_results = User.objects.filter(id = user)


	return render(request, 'loginPortal/volunteer_detail.html', {'query_results': query_results})