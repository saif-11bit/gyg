from ..forms import CustomSignupForm
from allauth.account.views import SignupView


class StudentSignupView(SignupView):
    template_name = "users/student_signup.html"
    form_class = CustomSignupForm
