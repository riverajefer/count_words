import smtplib

sender = "Private Person <webmaster@ptetime.com>"
receiver = "A Test User <jefersonpatino@yahoo.es>"

message = f"""\
Subject: Mensaje de prueba
To: {receiver}
From: {sender}

Hola Mundo."""

with smtplib.SMTP("smtp-relay.sendinblue.com", 2525) as server:
    server.login("riverajefer@gmail.com", "nhmGCy1tVYJN9Za4")
    server.sendmail(sender, receiver, message)