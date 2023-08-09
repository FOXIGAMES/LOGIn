from django.core.mail import send_mail

def send_confirmation_email(email, code):
    print(f"Sending confirmation email to {email} with code: {code}")
    send_mail(
        'Здравствуйте, активируйте ваш аккаунт!',
        f'Чтобы активировать ваш аккаунт, нажмите на ссылку:'
        f'\n{code}'
        f'\nНе передавайте ее никому.',
        'akusevtimur733@gmail.com',
        [email],
        fail_silently=False
    )
    print("Confirmation email sent.")

def send_email(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)

