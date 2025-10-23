# from django import forms
# from .models import Signup

# class SignupForm(forms.ModelForm):
#     confirm_password = forms.CharField(widget=forms.PasswordInput())

#     class Meta:
#         model = Signup
#         fields = ['name', 'email', 'mobile_number', 'password']
#         widgets = {
#             'password': forms.PasswordInput(),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm = cleaned_data.get("confirm_password")
#         if password != confirm:
#             raise forms.ValidationError("Passwords do not match")
#         return cleaned_data



import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Signup


class SignupForm(forms.ModelForm):
    # Name field – auto-capitalize handled in template via JS
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Full Name",
            "autocomplete": "off",
        }),
        label="Name"
    )

    # Email field
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Email Address",
            "autocomplete": "off",
        }),
        label="Email"
    )

    # Mobile number field
    mobile_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Mobile Number",
            "type": "tel",
            "pattern": "[6-9][0-9]{9}",
            "maxlength": "10",
            "inputmode": "numeric",
            "subject": "Enter a valid 10-digit mobile number starting with 6-9",
            "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",
        }),
        label="Mobile Number"
    )

    # Password
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password",
        }),
        label="Password"
    )

    # Confirm password
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password",
        }),
        label="Password Confirmation"
    )

    class Meta:
        model = Signup
        fields = ['name', 'email', 'mobile_number', 'password']

    def clean_mobile_number(self):
        """Server-side validation for 10-digit Indian mobile numbers"""
        mobile = self.cleaned_data.get("mobile_number")
        pattern = r'^[6-9]\d{9}$'
        if not re.match(pattern, mobile):
            raise ValidationError("Enter a valid 10-digit mobile number starting with 6-9.")
        return mobile

    def clean(self):
        """Ensure passwords match"""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        return cleaned_data

    def save(self, commit=True):
        """Hash password before saving"""
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# class LoginForm(forms.Form):
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    identifier = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Email or Name'}),
        label="Email or Name"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label="Password"
    )

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned


from django import forms
from .models import LocationAssignment, Signup

class LocationAssignmentForm(forms.ModelForm):
    class Meta:
        model = LocationAssignment
        fields = ['user', 'location', 'date']

    user = forms.ModelChoiceField(
        queryset=Signup.objects.all(),
        empty_label="Select User Name",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Exact Location'
        })
    )

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )



# from django import forms
# from .models import Meeting
# class MeetingForm(forms.ModelForm):
#     class Meta:
#         model = Meeting
#         fields = ['date', 'name', 'location', 'subject', 'agenda', 'event_time', 'duration']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'event_time': forms.TimeInput(attrs={'type': 'time'}),
#         }


from django import forms
from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'event_time': forms.TimeInput(attrs={'type': 'time'}),
            'endtime': forms.TimeInput(attrs={'type': 'time'}),
        }
