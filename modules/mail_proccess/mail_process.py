from flask_mail import Mail, Message
from flask import (
    Flask, render_template,
    request, redirect, url_for, abort,
    send_from_directory)

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '4122a92b0a6fd9'
app.config['MAIL_PASSWORD'] = '432fdd7cfbde13'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

class MailProccess():
    
    def send_mail(self, data_form, data_count_text):
        print('Start send mail! ')
        msg = Message('Formulario', sender='webmaster@ptetime.com',
                    recipients=['jefersonpatino@yahoo.es'])
        
        with app.app_context(), app.test_request_context():
            msg.html = render_template('template_email.html', data=data_form, data_count_text=data_count_text)
            mail.send(msg)
            print('Enviado !')