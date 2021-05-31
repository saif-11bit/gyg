from allauth.account.forms import SignupForm
from django import forms
from .models import Answer
 
 
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=100, label='First Name')
    last_name = forms.CharField(max_length=100, label='Last Name')
    # is_student = forms.BooleanField()
    is_teacher = forms.BooleanField(required=False)
 
    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.is_student = self.cleaned_data['is_student']
        user.is_teacher = self.cleaned_data['is_teacher']
        user.save()
        return user


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer_for', 'answer_by', 'answer_img', 'answer')
