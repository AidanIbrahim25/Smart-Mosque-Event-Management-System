from django.db import models


class Event(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]
    
    eventid = models.CharField(max_length=10, primary_key=True)
    eventname = models.CharField(max_length=100)
    eventdescription = models.TextField()
    eventdate = models.DateField()
    eventtime = models.TimeField()
    eventlocation = models.CharField(max_length=255)
    eventorganizer = models.CharField(max_length=100, null=True)
    max_attendees = models.PositiveIntegerField(null=True)  # number of people who can attend
    contact_number = models.CharField(max_length=15, null=True)  # organizer's phone number
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # event fee
    event_image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.eventname


class User(models.Model):
    userid=models.CharField(max_length=10, primary_key=True)
    user_name=models.TextField(max_length=100, null=True)
    userpassword = models.CharField(max_length=100, null=True)
    username=models.CharField(max_length=100,null=True)
    useremail=models.CharField(max_length=100)
    usernumber=models.CharField(max_length=12,null=True)
    userbirthdate=models.DateField(null=True)
    usergender=models.TextField(max_length=20,null=True)

class Admin(models.Model):
    adminid = models.CharField(max_length=10, primary_key=True)
    adminname = models.TextField(max_length=100)
    adminpassword = models.TextField(max_length=100)
    adminusername = models.TextField(max_length=100)
    adminemail = models.CharField(max_length=100, null=True)
    adminnumber = models.CharField(max_length=12)
    adminbirthdate = models.DateField() 
    admingender = models.TextField(max_length=20,null=True)
    adminrole = models.TextField(max_length=2)


class Registration(models.Model):
    registration_id = models.AutoField(primary_key=True)
    eventid = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)

    full_name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20,null=True, blank=True)
    ic_number = models.CharField(max_length=30,null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    num_attendees = models.PositiveIntegerField(default=1)
    special_requirements = models.TextField(blank=True, null=True)

    RSVP_CHOICES = [('YES', 'Yes'), ('NO', 'No'), ('MAYBE', 'Maybe')]
    rsvp_status = models.CharField(max_length=10, choices=RSVP_CHOICES, default='YES')

    PAYMENT_STATUS = [('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    STATUS_CHOICES = [('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    feedback = models.TextField(blank=True, null=True, help_text="User feedback about the event")

    class Meta:
        ordering = ['-registration_date']
        unique_together = ['eventid', 'userid']

    def __str__(self):
        return f"{self.full_name} ({self.userid.username}) - {self.eventid.eventname}"
