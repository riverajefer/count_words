<?php
//$to      = 'jefersonpatino@yahoo.es';
$to      = 'riverajefer@gmail.com';
$subject = 'Mensaje de prueba';
$message = 'Hola esto es un mensaje de prueba';
$headers = 'From: webmaster@ptetime.com' . "\r\n" .
    'Reply-To: webmaster@ptetime.com' . "\r\n" .
    'X-Mailer: PHP/' . phpversion();

mail($to, $subject, $message, $headers);
?>