from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Signup(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name



class LocationAssignment(models.Model):
    user = models.ForeignKey(Signup, on_delete=models.CASCADE, related_name="assignments")
    location = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.name} - {self.location_name} ({self.date})"

from django.utils import timezone
import random


class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        # OTP valid for 10 minutes
        return (timezone.now() - self.created_at).seconds <= 600




from django.db import models
from datetime import timedelta, datetime

class Meeting(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=200)  
    location = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True, null=True)
    agenda = models.TextField(blank=True, null=True)
    event_time = models.TimeField(blank=True, null=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in hours")
    endtime = models.TimeField(blank=True, null=True)
    referred_by = models.CharField(max_length=100, null=True, blank=True)
    place_of_event = models.CharField(max_length=200, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    invite_name = models.CharField(max_length=100, null=True, blank=True)


    def save(self, *args, **kwargs):
        """Auto-calc endtime from event_time + duration (hours)"""
        if self.event_time and self.duration:
            dt_start = datetime.combine(self.date, self.event_time)
            dt_end = dt_start + timedelta(hours=self.duration)
            self.endtime = dt_end.time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} @ {self.location} on {self.date}"

