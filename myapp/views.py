from django.shortcuts import render, redirect
from .models import Contact, User, Event, BookEvent
from django.conf import settings
from django.core.mail import send_mail
import random
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe
import requests

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

def validate_signup(request):
	email = request.GET.get('email')
	data = {
		'is_taken':User.objects.filter(email__iexact = email).exists()
	}
	return JsonResponse(data)

@csrf_exempt
def create_checkout_session(request):
	user=User.objects.get(email=request.session['email'])
	#amount = int(json.load(request)['post_data'])
	#be=int(json.load(request)['post_data1'])
	#print(be)
	data=json.load(request)
	amount=int(data['post_data'])
	be=int(data['post_data1'])
	bookevent=BookEvent.objects.get(pk=be)
	bookevent.payment_status=True
	bookevent.save()
	print(bookevent.user.fname)
	final_amount=amount*100
	
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'product_data': {
					'name': 'Checkout Session Data',
					},
				'unit_amount': final_amount,
				},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',)
	print(session.id)
	return JsonResponse({'id': session.id})

def success(request):
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')
# Create your views here.
def index(request):
	try:
		user = User.objects.get(email = request.session['email'])
		if user.usertype == "user":
			return render(request, 'index.html')
		else:
			return render(request, 'manager-index.html')
	except:
		return render(request, 'index.html')

def contact(request):
	if request.method == "POST":
		Contact.objects.create(
			name = request.POST['name'],
			email = request.POST['email'],
			phone = request.POST['phone'],	
			message = request.POST['message']
			)
		msg = "Contact Saved Successfully"
		return render(request, 'contact.html', {'msg':msg})
	else:
		return render(request, 'contact.html')

def signup(request):
	if request.method == "POST":
		try:
			User.objects.get(email = request.POST['email'])
			msg = "Email Already Registered"
			return render(request,  'signup.html', {'msg':msg})
		except:
			if request.POST['password'] == request.POST['cpassword']:
				User.objects.create(
					fname = request.POST['fname'],
					lname = request.POST['lname'],
					email = request.POST['email'],
					phone = request.POST['phone'],
					password = request.POST['password'],
					usertype = request.POST['usertype']
					)
				msg = "User Signup Successfully"
				return render(request, 'login.html', {'msg':msg})
			else:
				msg = "Password Does Not Match"
				return render(request, 'signup.html', {'msg':msg})
	else:
		return render(request, 'signup.html')

def shows_and_events(request):
	events = Event.objects.all()
	return render(request, 'shows-and-events.html', {'events':events})

def login(request):
	if request.method == "POST":
		try:
			user = User.objects.get(email = request.POST['email'])
			if user.password == request.POST['password']:
				request.session['email'] = user.email
				request.session['fname'] = user.fname
				request.session['profile_picture'] = user.profile_picture.url
				if user.usertype == "user":
					return render(request, 'index.html')
				else:
					return render(request, 'manager-index.html')
			else:
				msg = "Please Enter Correct Password"
				return render(request, 'login.html', {'msg':msg})
		except:
			msg = "User Does Not Exist"
			return render(request, 'login.html', {'msg':msg})
	else:
		return render(request, 'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.sessoin['fname']
		del request.session['profile_picture']
		msg = "User Logged Out Successfully"
		return render(request, 'login.html', {'msg':msg})
	except:
		msg = "User Logged Out Successfully"
		return render(request, 'login.html', {'msg':msg})
def change_password(request):
	user = User.objects.get(email = request.session['email'])
	if request.method == "POST":
		if user.password == request.POST['old_password']:
			if request.POST['new_password'] == request.POST['cnew_password']:
				user.password = request.POST['new_password']
				user.save()
				msg = "Password Changed Successfully"
				del request.session['email']
				del request.session['fname']
				return render(request, 'login.html', {'msg':msg})
			else:
				msg = "New Passwords Does Not Match"
				if user.usertype == "user":
					return render(request, 'change-password.html', {'msg':msg})
				else:
					return render(request, 'manager-change-password.html', {'msg':msg})
		else:
			msg = "Old Password Is Incorrect"
			if user.usertype == "user":
				return render(request, 'change-password.html', {'msg':msg})
			else:
				return render(request, 'manager-change-password.html', {'msg':msg})
	else:
		if user.usertype == "user":	
			return render(request, 'change-password.html')
		else:
			return render(request, 'manager-change-password.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(phone=request.POST['phone'])
			otp=str(random.randint(1000,9999))
			phone=str(request.POST['phone'])
			url = "https://www.fast2sms.com/dev/bulkV2"
			querystring = {"authorization":"cmMw2Ed6ZG8Ak1uQnWJxIBfg9e4hplvqV7yFLYSU3aijtKNTzC6UaiBNDxfKCM7rZ8F2kSOuwdpGePhT","variables_values":otp,"route":"otp","numbers":phone}
			headers = {'cache-control': "no-cache"}
			response = requests.request("GET", url, headers=headers, params=querystring)
			print(response.text)
			return render(request,'otp.html',{'otp':otp,'phone':phone})
		except Exception as e:
			print(e)
			msg="Mobile Not Registered"
			return render(request,'forgot-password.html',{'msg':msg})
	else:
		return render(request,'forgot-password.html')

def verify_otp(request):
	otp = request.POST['otp']
	uotp = request.POST['uotp']
	phone = request.POST['phone']

	if otp == uotp:
		return render(request, 'new-password.html', {'phone':phone})
	else:
		msg = "Invalid OTP"
		return render(request, 'otp.html', {'phone':phone, 'otp':otp, 'msg':msg})

def new_password(request):
	phone = request.POST['phone']
	np = request.POST['new_password']
	cnp = request.POST['cnew_password']

	if np == cnp:
		user = User.objects.get(phone=phone)
		user.password = np 
		user.save()
		msg = "Password Updated Successfully"
		return render(request, 'login.html', {'msg':msg})
	else:
		msg = "Passwords Does Not Match"
		return render(request, 'new-password.html', {'phone':phone, 'msg':msg})

def profile(request):
	user = User.objects.get(email = request.session['email'])
	if request.method == "POST":
		user.fname = request.POST['fname']
		user.lname = request.POST['lname']
		user.phone = request.POST['phone']
		try:
			user.profile_picture = request.FILES['profile_picture']
		except:
			pass
		user.save()
		request.session['profile_picture'] = user.profile_picture.url
		request.session['fname'] = user.fname
		msg = "Profile Updated Successfully"
		if user.usertype == "user":
			return render(request, 'profile.html', {'user':user, 'msg':msg})
		else:
			return render(request, 'manager-profile.html', {'user':user, 'msg':msg})
	else:
		if user.usertype == "user":
			return render(request, 'profile.html', {'user':user})
		else:
			return render(request, 'manager-profile.html', {'user':user})

def manager_add_event(request):
	if request.method == "POST":
		manager = User.objects.get(email = request.session['email'])
		Event.objects.create(
			manager = manager,
			event_name = request.POST['event_name'],
			event_date = request.POST['event_date'],
			event_time = request.POST['event_time'],
			event_venue = request.POST['event_venue'],
			event_price = request.POST['event_price'],
			event_picture = request.FILES['event_picture']
			)
		msg = "Event Added Successfully"
		return render(request, 'manager-add-event.html', {'msg':msg})
	else:
		return render(request, 'manager-add-event.html')

def manager_view_event(request):
	manager = User.objects.get(email = request.session['email'])
	events = Event.objects.filter(manager = manager)
	return render(request, 'manager-view-event.html', {'events':events})

def manager_edit_event(request, pk):
	event = Event.objects.get(pk = pk)
	if request.method == "POST":
		event.event_name = request.POST['event_name']
		event.event_date = request.POST['event_date']
		event.event_time = request.POST['event_time']
		event.event_venue = request.POST['event_venue']
		event.event_price = request.POST['event_price']
		try:
			event.event_picture = request.FILES['event_picture']
		except:
			pass
		event.save()
		msg = "Event Updated Successfully"
		return render(request, 'manager-edit-event.html', {'event':event, 'msg':msg})
	else:
		return render(request, 'manager-edit-event.html', {'event':event})

def manager_delete_event(request, pk):
	event = Event.objects.get(pk = pk)
	event.delete()
	return redirect('manager-view-event')

def book_event(request, pk):
	event = Event.objects.get(pk = pk)
	user = User.objects.get(email = request.session['email'])
	if request.method == "POST":
		BookEvent.objects.create(
			user = user,
			event = event,
			event_price = event.event_price,
			ticket_qty = int(request.POST['ticket_qty']),
			total_price = event.event_price*int(request.POST['ticket_qty'])
			)
		msg = "Event Booked Successfully"
		events = BookEvent.objects.filter(user = user)
		return render(request, 'myevents.html', {'events':events, 'msg':msg})
	else:
		return render(request, 'book-event.html', {'event':event, 'user':user})

def myevents(request):
	user = User.objects.get(email = request.session['email'])
	events = BookEvent.objects.filter(user = user)
	return render(request, 'myevents.html', {'events':events})

def payment(request, pk):
	bookevent = BookEvent.objects.get(pk = pk)
	total_price = bookevent.total_price
	be=bookevent.pk
	print("BE : ",be)
	return render(request, 'payment.html', {'bookevent':bookevent, 'total_price':total_price, 'be':be})