from django import forms
class login2(forms.Form):
    Username = forms.CharField()
    Password = forms.CharField(widget=forms.PasswordInput())
