import pytz
import time
from datetime import datetime, timezone

class ProccessRquest():
    
    def on_proccess_request(self, request):
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