from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
import os
    
def send_verification_email(request, user, mail_subject, email_template):
    current_site = get_current_site(request)
    from_email = settings.DEFAULT_FROM_EMAIL
    context = {
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':default_token_generator.make_token(user),
    }
    message = render_to_string(email_template, context)
    mail = EmailMessage(mail_subject, message, from_email, to=[user.email])
    mail.send()


   # 'emails/reset_password_validate.html'
'''    
def send_notification(mail_subject, email_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    user = context['user']
    mail = EmailMessage(mail_subject, message, from_email, to=[user.email])
    mail.send()'''

def image_validator(value):
    extention = os.path.splitext(value.name)[1]
    valid_extentions = ['.png', '.jpeg', '.jpg',]
    if not extention.lower() in valid_extentions:
        raise ValidationError('Unsupported file type, upload supported file type: '+ str(valid_extentions))
    