from flask_mail import Mail, Message
import os
import magic
from flask import (
    Flask, render_template,
    request, redirect, url_for, abort,
    send_from_directory)

from werkzeug.utils import secure_filename
app = Flask(__name__)


''' app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '4122a92b0a6fd9'
app.config['MAIL_PASSWORD'] = '432fdd7cfbde13'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
 '''


app.config['MAIL_SERVER'] = 'mail.translative.com.co'
app.config['MAIL_PORT'] = 290
app.config['MAIL_USERNAME'] = 'contact@translative.com.co'
app.config['MAIL_PASSWORD'] = 'E(qNFJCICpm_'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
FILE_OUTPUT_TEXT_PLAIM = '/home/Flask/count_words/files/output.txt'

class MailProccess():
    
    def send_mail(self, data_form, data_count_text, file):
        
        print('Start send mail! ')
        filename = secure_filename(file.filename)
        path_file = os.path.abspath(filename)
        mime = magic.Magic(mime=True)
        content_type = mime.from_file(path_file)
        
        msg = Message('Formulario', sender='do-not-reply@translative.com.co',
                    recipients=['jefersonpatino@yahoo.es', 'contact@translative.com.co'])
        
        with app.app_context(), app.test_request_context():
            msg.html = render_template('template_email.html', data=data_form, data_count_text=data_count_text)
            
            with app.open_resource(path_file) as fp:
                msg.attach(filename = file.filename, content_type = content_type, data = fp.read())
            
            with app.open_resource(FILE_OUTPUT_TEXT_PLAIM) as fp:
                msg.attach(filename = "transcript", content_type ="text/plain", data = fp.read())
                
            mail.send(msg)
            app.logger.info('Email enviado !')
            print('Enviado !')
            
    def send_mail_client(self, email_client):
        print('Start send mail Client! ')
        msg = Message('Translative.com.co Formulario', sender='do-not-reply@translative.com.co',
                    recipients=[email_client])
        
        with app.app_context(), app.test_request_context():
            msg.html = render_template('mail_client.html')
            mail.send(msg)
            app.logger.info('Email enviado !')
            print('Enviado !')