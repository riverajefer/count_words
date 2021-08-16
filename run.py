'''
165.232.156.205:5000
'''
import os
import pytz
import time
from datetime import datetime, timezone
from flask import jsonify
import threading
from flask import (
    Flask, render_template,
    request, redirect, url_for, abort,
    send_from_directory)

from modules.counter_words.count_words import CountWordsDocument
from modules.mail_proccess.mail_process import MailProccess


app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form_count', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        return CountWordsDocument().on_start_count(file=file)
    
    return render_template('form_count.html')
    

def on_proccess_request(request):
    tz = pytz.timezone('America/Bogota')
    bogota_now = datetime.now(tz)

    name = request.form['name']
    business = request.form['business']
    jobPosition = request.form['jobPosition']
    country = request.form['country']
    state = request.form['state']
    city = request.form['city']
    phone = request.form['phone']
    email = request.form['email']
    message = request.form['message']
    dateDelivery = request.form['dateDelivery']
    lang_from = request.form['lang_from']
    lang_to = request.form['lang_to']

    data_form = {
        'name': name,
        'business': business,
        'jobPosition': jobPosition,
        'country': country,
        'state': state,
        'city': city,
        'phone': phone,
        'email': email,
        'message': message,
        'dateDelivery': dateDelivery,
        'lang_from': lang_from,
        'lang_to': lang_to,
        'now': bogota_now
    }
    print(data_form)

    return data_form


def on_proccess_text_and_send_mail(file, data_form):
    data_count_text = CountWordsDocument().on_start_count(file=file)
    MailProccess().send_mail(data_form=data_form, data_count_text=data_count_text)


@app.route('/form_client', methods=['GET','POST'])
def form_client():
    if request.method == 'POST':
        data_form = on_proccess_request(request=request)
        file = request.files['file']
        
        threading.Thread(target=on_proccess_text_and_send_mail, daemon=True, args=[file,data_form]).start()
        
        while threading.activeCount() >1:
            time.sleep(5)
            data = {
                'success': True
            }
            print(data)
            return jsonify(data)
   

    return render_template('form_client.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")

