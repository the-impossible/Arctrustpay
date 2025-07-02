# Django imports
from django.shortcuts import render, redirect
from django.views.generic import *
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


# My app imports
from trustpay_landing.models import *
from trustpay_landing.forms import *
from trustpay_email.mailer import *

# Create your views here.
class HomeView(TemplateView):
    template_name = "frontend/home.html"

class ContactUsView(View, SuccessMessageMixin):

    template_name = "frontend/contact.html"
    form = ContactUsForm

    def get(self, request):

        context = {
            'form':self.form,
        }

        return render(request, self.template_name, context)

    def post(self, request):

        form = self.form(request.POST)

        if form.is_valid():

            form.save()
            messages.success(request, 'Your message has been received, we will revert shortly.')

            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            user_details = {
                'email':email,
                'name':name,
                'subject': subject,
                'message':message,
            }

            Email.send(user_details, 'request_support')

            return redirect('landing:contact')

        else:

            messages.success(request, form.errors.as_text())

            context = {
                'form':form,
            }

            return render(request, self.template_name, context)

class AboutUsView(TemplateView):
    template_name = "frontend/about.html"

class ServicesView(TemplateView):
    template_name = "frontend/services.html"