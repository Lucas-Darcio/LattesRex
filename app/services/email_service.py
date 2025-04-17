import smtplib
from email.message import EmailMessage
import json

def send_email(to_address, evaluation_data):
    from_address = "no-reply@example.com"
    subject = "LLM Response and Evaluation"

    # Converte os dados da avaliação para formato legível
    body = json.dumps(evaluation_data, indent=4)

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address

    # Envio do e-mail usando SMTP
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login(from_address, "your_password")
        server.send_message(msg)