'''
165.232.156.205:5000
'''
import os
import time
from flask import jsonify
import threading
from flask import (Flask, render_template, request)

from modules.counter_words.count_words import CountWordsDocument
from modules.mail_proccess.mail_process import MailProccess
from modules.proccess_request.proccess_request import ProccessRquest

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form_count', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        return CountWordsDocument().on_start_count(file=file)

    return render_template('form_count.html')


def on_proccess_text_and_send_mail(file, data_form):
    data_count_text = CountWordsDocument().on_start_count(file=file)
    MailProccess().send_mail(data_form=data_form, data_count_text=data_count_text)


@app.route('/form_client', methods=['GET', 'POST'])
def form_client():
    if request.method == 'POST':
        data_form = ProccessRquest().on_proccess_request(request=request)
        file = request.files['file']

        threading.Thread(target=on_proccess_text_and_send_mail,
                         daemon=True, args=[file, data_form]).start()

        while threading.activeCount() > 1:
            time.sleep(5)
            data = {
                'success': True
            }
            print(data)
            return jsonify(data)

    return render_template('form_client.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")
