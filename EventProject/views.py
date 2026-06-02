from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
import uuid
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from django.shortcuts import render

from .models import User, Admin, Event, Registration


# Create your views here.
def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def aboutuser(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    user = User.objects.get(username=username)
    return render(request, "aboutuser.html", {'user': user})

def loginpageuser(request):
    if request.method =='POST':
        username=request.POST['username']
        userpassword=request.POST['userpassword']
        
        try:
            user = User.objects.get(username=username)
            
            if user.userpassword == userpassword:
                request.session['username'] = user.username
                return redirect("indexuser/")
            else:
                dict={ 
                    "message":"Wrong Password"
                    }
                return render (request, 'loginpageuser.html',dict)
                
        except User.DoesNotExist:
            dict={
                "message":"Wrong Username"
                }
            return render (request, 'loginpageuser.html',dict)
        
    else:
        dict={ 
            'message':''
            }
        return render (request, 'loginpageuser.html',dict)

def indexuser(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = User.objects.get(username=username)
    today = timezone.now().date()

    events = Event.objects.all().order_by('-eventdate', '-eventtime')

    user_regs = Registration.objects.filter(userid=user)
    reg_map = {reg.eventid_id: reg for reg in user_regs}

    dashboard_events = []
    total_completed = 0
    total_attendance = 0
    for event in events:
        reg = reg_map.get(event.eventid)
        if reg:
            reg_status = reg.status
            registered = True
            total_attendance += reg.num_attendees if reg.num_attendees else 1
        else:
            reg_status = None
            registered = False
        is_completed = event.status == 'COMPLETED' or event.eventdate < today
        if registered and is_completed:
            total_completed += 1
        dashboard_events.append({
            'event': event,
            'registered': registered,
            'registration': reg,
            'registration_status': reg_status,
            'is_completed': is_completed,
        })

    dashboard_events = [item for item in dashboard_events if item['registered']]

    total_registered = len(dashboard_events)

    context = {
        'dashboard_events': dashboard_events,
        'user': user,
        'total_events': len(dashboard_events),
        'total_completed': total_completed,
        'total_attendance': total_attendance,
        'total_registered': total_registered,
    }
    return render(request, "indexuser.html", context)

def indexadmin(request):
    adminusername = request.session.get('adminusername')
    if not adminusername:
        return redirect('loginpageadmin')
        
    admin = Admin.objects.filter(adminusername=adminusername).first()
    
    total_events = Event.objects.count()
    total_attendees = Registration.objects.count()
    
    today = timezone.now().date()
    
    status = request.GET.get('status', '')
    
    events = Event.objects.all()
    
    if status == 'upcoming':
        events = events.filter(eventdate__gte=today)
    elif status == 'past':
        events = events.filter(eventdate__lt=today)
    
    events = events.order_by('eventdate', 'eventtime')
    
    pending_registrations = Registration.objects.filter(status='PENDING').count()
    
    upcoming_events = Event.objects.filter(eventdate__gte=today)

    context = {
        'admin': admin,
        'adminusername': adminusername,
        'total_events': total_events,
        'total_attendees': total_attendees,
        'events': events,
        'upcoming_events': upcoming_events,
        'pending_registrations': pending_registrations,
        'today': today,
        'status': status
    }

    return render(request, "admindashboard.html", context)

def admindashboard(request):
    adminusername = request.session.get('adminusername')
    if not adminusername:
        return redirect('loginpageadmin')
        
    admin = Admin.objects.filter(adminusername=adminusername).first()
    
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        action = request.POST.get('action')
        
        if event_id and action:
            try:
                event = Event.objects.get(eventid=event_id)
                
                if action == 'delete':
                    event.delete()
                    messages.success(request, 'Event deleted successfully.')
                elif action == 'complete':
                    event.status = 'COMPLETED'
                    event.save()
                    messages.success(request, 'Event marked as completed.')
                elif action == 'upcoming':
                    event.status = 'UPCOMING'
                    event.save()
                    messages.success(request, 'Event marked as upcoming.')
                elif action == 'cancel':
                    event.status = 'CANCELLED'
                    event.save()
                    messages.success(request, 'Event cancelled.')
                
                return redirect('admindashboard')
            except Event.DoesNotExist:
                messages.error(request, 'Event not found.')
    
    total_events = Event.objects.count()
    total_attendees = Registration.objects.count()
    
    today = timezone.now().date()
    
    status = request.GET.get('status', '')
    
    events = Event.objects.all()
    
    if status == 'upcoming':
        events = events.filter(status='UPCOMING')
    elif status == 'completed':
        events = events.filter(status='COMPLETED')
    elif status == 'cancelled':
        events = events.filter(status='CANCELLED')
    
    events = events.order_by('eventdate', 'eventtime')
    
    pending_registrations = Registration.objects.filter(status='PENDING').count()
    
    upcoming_events = Event.objects.filter(status='UPCOMING')
    
    completed_events = Event.objects.filter(status='COMPLETED')

    context = {
        'admin': admin,
        'adminusername': adminusername,
        'total_events': total_events,
        'total_attendees': total_attendees,
        'events': events,
        'upcoming_events': upcoming_events,
        'completed_events': completed_events,
        'pending_registrations': pending_registrations,
        'today': today,
        'status': status
    }

    return render(request, "admindashboard.html", context)

def login(request):
    return render(request, "login.html")

def loginpageadmin(request):
    if request.method =='POST':
        adminusername=request.POST['adminusername']
        adminpassword=request.POST['adminpassword']
        
        try:
            admin = Admin.objects.get(adminusername=adminusername)
            
            if admin.adminpassword == adminpassword:
                request.session['adminusername'] = admin.adminusername
                return redirect("indexadmin/")
            else:
                dict={ 
                    "message":"Wrong Password"
                    }
                return render (request, 'loginpageadmin.html',dict)
                
        except Admin.DoesNotExist:
            dict={
                "message":"Wrong Username"
                }
            return render (request, 'loginpageadmin.html',dict)
        
    else:
        dict={ 
            'message':''
            }
        return render (request, 'loginpageadmin.html',dict)

def signup(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        user_name = request.POST.get('user_name')
        useremail = request.POST.get('useremail')
        usernumber = request.POST.get('usernumber')
        userbirthdate = request.POST.get('userbirthdate')
        usergender = request.POST.get('usergender')
        username = request.POST.get('username')
        userpassword = request.POST.get('userpassword')  # Use the correct name for the password field
        confirm_password = request.POST.get('confirm_password')

        if userpassword != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        user_data = User(
            userid=userid,
            user_name=user_name,
            useremail=useremail,
            usernumber=usernumber,
            userbirthdate=userbirthdate,
            usergender=usergender,
            username=username,
            userpassword=userpassword,  
        )
        user_data.save()
        
        messages.success(request, "Signup successful! You can now log in.")
        return redirect('login')  

    return render(request, "signup.html")

def event(request):
    events = Event.objects.all().order_by('-eventdate', '-eventtime')
    context = {
        'events': events
    }
    return render(request, 'event.html', context)

def eventuser(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    user = User.objects.get(username=username)
    
    events = Event.objects.all().order_by('-eventdate', '-eventtime')
    
    user_registrations = Registration.objects.filter(userid=user)
    reg_map = {reg.eventid_id: reg for reg in user_registrations}
    
    events_with_status = []
    for event in events:
        registration = reg_map.get(event.eventid)
        events_with_status.append({
            'event': event,
            'registration': registration,
            'is_registered': registration is not None
        })
    
    context = {
        'events': events_with_status,
        'user': user,
    }
    return render(request, 'eventuser.html', context)

def userregistrations(request, event_id):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'Please login first to view registrations.')
        return redirect('login')
    
    user = User.objects.get(username=username)
    event = get_object_or_404(Event, eventid=event_id)
    
    registration = Registration.objects.filter(eventid=event, userid=user).first()
    
    if request.method == 'POST' and registration:
        registration.full_name = request.POST.get('name')
        registration.email = request.POST.get('email')
        registration.phone = request.POST.get('phone')
        registration.ic_number = request.POST.get('ic_number')
        registration.address = request.POST.get('address')
        registration.rsvp_status = request.POST.get('rsvp_status')
        registration.num_attendees = request.POST.get('num_attendees') or 1
        registration.special_requirements = request.POST.get('special_requirements')
        registration.payment_reference = request.POST.get('payment_method')
        registration.payment_amount = request.POST.get('total_fee') or 0
        registration.payment_status = request.POST.get('paid_status')
        registration.feedback = request.POST.get('feedback')
        registration.save()
        messages.success(request, 'Your registration has been updated successfully!')
        return redirect('eventuser')
    
    context = {
        'event': event,
        'user': user,
        'registration': registration,
        'is_registered': registration is not None
    }
    return render(request, 'userregistrations.html', context)

def realregistrations(request, event_id):
    """View to handle event registration form and display"""
    event = get_object_or_404(Event, eventid=event_id)
    
    username = request.session.get('username')
    if not username:
        messages.error(request, 'Please login first to register for events.')
        return redirect('login')
    
    user = User.objects.get(username=username)
    
    existing_registration = Registration.objects.filter(eventid=event, userid=user).first()
    if existing_registration:
        messages.warning(request, f'You have already registered for "{event.eventname}". You cannot register for the same event twice.')
        return redirect('eventuser')
    
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        ic_number = request.POST.get('ic_number')
        address = request.POST.get('address')
        rsvp_status = request.POST.get('rsvp_status')
        num_attendees = int(request.POST.get('num_attendees', 1))
        special_requirements = request.POST.get('special_requirements', '')
        payment_method = request.POST.get('payment_method')
        total_fee = request.POST.get('total_fee')
        paid_status = request.POST.get('paid_status')
        feedback = request.POST.get('feedback', '')
        
        registration = Registration.objects.create(
            eventid=event,
            userid=user,  
            full_name=full_name,
            email=email,
            phone=phone,
            ic_number=ic_number,
            address=address,
            num_attendees=num_attendees,
            special_requirements=special_requirements,
            rsvp_status=rsvp_status,
            status='PENDING',
            payment_status=paid_status if paid_status else 'PENDING',
            feedback=feedback
        )
        
        messages.success(request, 'Your registration has been submitted successfully!')
        return redirect('eventuser')
    
    context = {
        'event': event,
        'user': user,  
    }
    return render(request, 'realregistrations.html', context)

def adminreport(request):
    """View to display all registrations in the admin report"""
    adminusername = request.session.get('adminusername')
    if not adminusername:
        return redirect('loginpageadmin')
    
    event_filter = request.GET.get('event', '')
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    
    registrations = Registration.objects.all().select_related('eventid', 'userid')
    
    if event_filter:
        registrations = registrations.filter(eventid__eventid=event_filter)
    if status_filter:
        registrations = registrations.filter(status=status_filter)
    if payment_filter:
        registrations = registrations.filter(payment_status=payment_filter)
    
    events = Event.objects.all()
    
    status_counts = {
        'PENDING': registrations.filter(status='PENDING').count(),
        'CONFIRMED': registrations.filter(status='CONFIRMED').count(),
        'CANCELLED': registrations.filter(status='CANCELLED').count(),
    }

    payment_counts = {
        'PAID': registrations.filter(payment_status='PAID').count(),
        'NOT_PAID': registrations.filter(payment_status='NOT_PAID').count(),
    }
    
    context = {
        'registrations': registrations.order_by('-registration_date'),
        'adminusername':adminusername,
        'events': events,
        'selected_event': event_filter,
        'selected_status': status_filter,
        'selected_payment': payment_filter,
        'status_counts': status_counts,
        'payment_counts': payment_counts,
        'total_registrations': registrations.count(),
    }
    return render(request, 'adminreport.html', context)

def update_registration_status(request, registration_id):
    """Update the status of a registration"""
    if not request.session.get('adminusername'):
        return redirect('loginpageadmin')
    
    if request.method == 'POST':
        registration = get_object_or_404(Registration, pk=registration_id)
        
        new_status = request.POST.get('status')
        new_rsvp_status = request.POST.get('rsvp_status')
        new_payment_status = request.POST.get('payment_status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(Registration.STATUS_CHOICES):
            registration.status = new_status
        
        if new_rsvp_status in dict(Registration.RSVP_CHOICES):
            registration.rsvp_status = new_rsvp_status
        
        if new_payment_status in dict(Registration.PAYMENT_STATUS):
            registration.payment_status = new_payment_status
            if new_payment_status == 'PAID':
                registration.payment_date = timezone.now()
        
        registration.save()
        
        messages.success(request, f'Registration status updated successfully for {registration.full_name}.')
        
        return redirect('adminregistration', event_id=registration.eventid.eventid)
    
    registration = get_object_or_404(Registration, pk=registration_id)
    return redirect('adminregistration', event_id=registration.eventid.eventid)

def eventadmin(request):
    adminusername = request.session.get('adminusername')
    if not adminusername:
        return redirect('login')

    if request.method == 'POST':
        action = request.POST.get('action')
        event_id = request.POST.get('event_id')
        
        if action and event_id:
            try:
                event = Event.objects.get(eventid=event_id)
                
                if action == 'complete':
                    event.status = 'COMPLETED'
                    event.save()
                    messages.success(request, f'Event "{event.eventname}" marked as completed.')
                elif action == 'delete':
                    event_name = event.eventname
                    event.delete()
                    messages.success(request, f'Event "{event_name}" deleted successfully.')
                
                return redirect('eventadmin')
            except Event.DoesNotExist:
                messages.error(request, 'Event not found.')
                return redirect('eventadmin')
        # Only create a new event if no action is present
        if not action:
            eventid = request.POST.get('eventid')
            eventname = request.POST.get('eventname')
            eventdescription = request.POST.get('eventdescription')
            eventdate = request.POST.get('eventdate')
            eventtime = request.POST.get('eventtime')
            eventlocation = request.POST.get('eventlocation')
            eventorganizer = request.POST.get('eventorganizer')
            max_attendees_str = request.POST.get('max_attendees')
            contact_number = request.POST.get('contact_number')
            event_image = request.FILES.get('event_image')  

            max_attendees = None
            if max_attendees_str and max_attendees_str.isdigit():
                max_attendees = int(max_attendees_str)

            Event.objects.create(
                eventid=eventid,
                eventname=eventname,
                eventdescription=eventdescription,
                eventdate=eventdate,
                eventtime=eventtime,
                eventlocation=eventlocation,
                eventorganizer=eventorganizer,
                max_attendees=max_attendees,
                contact_number=contact_number,
                event_image=event_image  
            )
            return redirect('eventadmin')

    query = request.GET.get('q')
    filter_status = request.GET.get('filter')
    
    events = Event.objects.all()
    
    if query:
        events = events.filter(eventname__icontains=query)
    
    if filter_status == 'upcoming':
        events = events.filter(status='UPCOMING')
    elif filter_status == 'completed':
        events = events.filter(status='COMPLETED')

    events = events.order_by('-eventdate', '-eventtime')

    context = {
        'events': events,
        'adminusername': adminusername
    }
    return render(request, 'eventadmin.html', context)

def adminaccount(request):
    if 'adminusername' not in request.session:
        return redirect('adminlogin')
    
    admin = Admin.objects.get(adminusername=request.session['adminusername'])
    edit_mode = request.GET.get('edit') == 'true'
    
    if request.method == 'POST':
        try:
            if admin.adminpassword != request.POST['adminpassword']:
                messages.error(request, 'Current password is incorrect')
                return redirect('adminaccount')
            
            admin.adminname = request.POST['adminname']
            admin.adminusername = request.POST['adminusername']
            admin.adminemail = request.POST['adminemail']
            admin.adminnumber = request.POST['adminnumber']
            admin.adminbirthdate = request.POST['adminbirthdate']
            admin.admingender = request.POST['admingender']
            
            new_password = request.POST.get('new_password')
            if new_password:
                admin.adminpassword = new_password
            
            admin.save()
            
            request.session['adminusername'] = admin.adminusername
            
            messages.success(request, 'Account information updated successfully')
            return redirect('adminaccount')
            
        except Exception as e:
            messages.error(request, f'Error updating account: {str(e)}')
            return redirect('adminaccount')
    
    return render(request, 'adminaccount.html', {
        'admin': admin,
        'edit_mode': edit_mode,
        'adminusername': request.session['adminusername']
    })

def adminregistration(request, event_id):
    """View to display registrations for a specific event"""
    if not request.session.get('adminusername'):
        return redirect('loginpageadmin')

    event = get_object_or_404(Event, eventid=event_id)
    
    registrations = Registration.objects.filter(eventid=event).select_related('userid')
    
    status_counts = {
        'PENDING': registrations.filter(status='PENDING').count(),
        'CONFIRMED': registrations.filter(status='CONFIRMED').count(),
        'CANCELLED': registrations.filter(status='CANCELLED').count(),
    }
    
    total_attendees = sum(reg.num_attendees for reg in registrations)
    
    context = {
        'event': event,
        'registrations': registrations.order_by('-registration_date'),
        'status_counts': status_counts,
        'total_registrations': registrations.count(),
        'total_attendees': total_attendees,
        'adminusername': request.session.get('adminusername')
    }
    
    return render(request, 'adminregistration.html', context)

def admineditevent(request, event_id):
    adminusername = request.session.get('adminusername')
    if not adminusername:
        return redirect('loginpageadmin')
    
    event = get_object_or_404(Event, eventid=event_id)
    
    if request.method == 'POST':
        event.eventname = request.POST.get('eventname')
        event.eventdescription = request.POST.get('eventdescription')
        event.eventdate = request.POST.get('eventdate')
        event.eventtime = request.POST.get('eventtime')
        event.eventlocation = request.POST.get('eventlocation')
        event.eventorganizer = request.POST.get('eventorganizer')
        event.max_attendees = request.POST.get('max_attendees')
        event.contact_number = request.POST.get('contact_number')
        event.fee = request.POST.get('fee', 0.00)
        
        if 'event_image' in request.FILES:
            event.event_image = request.FILES['event_image']
        
        try:
            event.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('eventadmin')
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    context = {
        'event': event,
        'adminusername': adminusername
    }
    
    return render(request, 'admineditevent.html', context)

def useraccount(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    user = User.objects.get(username=username)
    edit_mode = request.GET.get('edit') == 'true'

    if request.method == 'POST':
        try:
            user.user_name = request.POST.get('user_name')
            user.username = request.POST.get('username')
            user.useremail = request.POST.get('useremail')
            user.usernumber = request.POST.get('usernumber')
            user.userbirthdate = request.POST.get('userbirthdate')
            user.usergender = request.POST.get('usergender')

            new_password = request.POST.get('new_password')
            if new_password:
                user.userpassword = new_password

            user.save()

            messages.success(request, 'Account information updated successfully')
            return redirect('useraccount')

        except Exception as e:
            messages.error(request, f'Error updating account: {str(e)}')
            return redirect('useraccount')

    return render(request, 'useraccount.html', {
        'user': user,
        'edit_mode': edit_mode
    })

def admincreateevent(request):
    adminusername = request.session.get('adminusername')
    if not adminusername:
        return redirect('loginpageadmin')
    
    if request.method == 'POST':
        event_id = request.POST.get('eventid')
        
        event = Event(
            eventid=event_id,
            eventname=request.POST.get('eventname'),
            eventdescription=request.POST.get('eventdescription'),
            eventdate=request.POST.get('eventdate'),
            eventtime=request.POST.get('eventtime'),
            eventlocation=request.POST.get('eventlocation'),
            eventorganizer=request.POST.get('eventorganizer'),
            max_attendees=request.POST.get('max_attendees'),
            contact_number=request.POST.get('contact_number'),
            fee=request.POST.get('fee', 0.00),
            status='UPCOMING'
        )
        
        if 'event_image' in request.FILES:
            event.event_image = request.FILES['event_image']
        
        event.save()
        messages.success(request, 'Event created successfully!')
        return redirect('admindashboard')
    
    return render(request, 'admincreateevent.html', {'adminusername': adminusername})

def adminfeedback(request):
    adminusername = request.session.get('adminusername')
    if not adminusername:
        return redirect('loginpageadmin')
    
    selected_event = request.GET.get('event', '')
    date_range = request.GET.get('date_range', '')
    
    feedbacks = Registration.objects.filter(feedback__isnull=False).exclude(feedback='').select_related('eventid', 'userid')
    
    if selected_event:
        feedbacks = feedbacks.filter(eventid__eventid=selected_event)
    
    from datetime import datetime, timedelta
    today = datetime.now().date()
    
    if date_range == 'today':
        feedbacks = feedbacks.filter(registration_date__date=today)
    elif date_range == 'week':
        week_ago = today - timedelta(days=7)
        feedbacks = feedbacks.filter(registration_date__date__gte=week_ago)
    elif date_range == 'month':
        month_ago = today - timedelta(days=30)
        feedbacks = feedbacks.filter(registration_date__date__gte=month_ago)
    elif date_range == 'year':
        year_ago = today - timedelta(days=365)
        feedbacks = feedbacks.filter(registration_date__date__gte=year_ago)
    
    feedbacks = feedbacks.order_by('-registration_date')
    
    events = Event.objects.all().order_by('-eventdate')
    
    total_feedback = Registration.objects.filter(feedback__isnull=False).exclude(feedback='').count()
    events_with_feedback = Event.objects.filter(registrations__feedback__isnull=False).exclude(registrations__feedback='').distinct().count()
    unique_users = Registration.objects.filter(feedback__isnull=False).exclude(feedback='').values('userid').distinct().count()
    recent_feedback = Registration.objects.filter(
        feedback__isnull=False,
        registration_date__date__gte=today - timedelta(days=7)
    ).exclude(feedback='').count()
    
    context = {
        'feedbacks': feedbacks,
        'events': events,
        'selected_event': selected_event,
        'date_range': date_range,
        'total_feedback': total_feedback,
        'events_with_feedback': events_with_feedback,
        'unique_users': unique_users,
        'recent_feedback': recent_feedback,
        'adminusername': adminusername
    }
    
    return render(request, 'adminfeedback.html', context)

def registrations(request, event_id):
    return render(request, 'registrations.html', {'event_id': event_id})

def adminviewregistrations(request, registration_id):
    """View to display detailed information about a specific registration"""
    
    if not request.session.get('adminusername'):
        return redirect('loginpageadmin')
    
    registration = get_object_or_404(Registration, registration_id=registration_id)
    
    event = registration.eventid
    
    context = {
        'registration': registration,
        'event': event,
        'adminusername': request.session.get('adminusername')
    }
    
    return render(request, 'adminviewregistrations.html', context)

@require_POST
def ajax_delete_event(request):
    event_id = request.POST.get('event_id')
    if not event_id:
        return JsonResponse({'success': False, 'error': 'No event_id provided.'}, status=400)
    try:
        event = Event.objects.get(eventid=event_id)
        event.delete()
        return JsonResponse({'success': True})
    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Event not found.'}, status=404)