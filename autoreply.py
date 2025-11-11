# email_autoreply.py
import g4f
import imaplib
import email
import smtplib
from email.mime.text import MIMEText

EMAIL_ACCOUNT = "your_email@gmail.com"  # Ваша почта
EMAIL_PASSWORD = "your_app_password"    # Пароль приложения Gmail
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def generate_email_reply(incoming_email: str) -> str:
    """Генерация ответа на письмо с помощью g4f"""
    prompt = f"""Ты — профессиональный ассистент по деловой переписке.
Ответь кратко, структурировано и вежливо.
Формат:
1. Благодарность за обращение.
2. Ответ по сути.
3. Предложение следующего шага.

Письмо клиента:
"""{incoming_email}""""""
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
            timeout=60
        )
        return response if isinstance(response, str) else str(response)
    except Exception as e:
        return f"Ошибка генерации: {e}"

def fetch_latest_email():
    """Получение последнего непрочитанного письма"""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select('inbox')
    result, data = mail.search(None, 'UNSEEN')
    mail_ids = data[0].split()
    if not mail_ids:
        print("Нет новых писем.")
        return None, None
    latest_email_id = mail_ids[-1]
    result, data = mail.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)
    from_email = email.utils.parseaddr(msg['From'])[1]
    subject = msg['Subject']
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body += part.get_payload(decode=True).decode()
    else:
        body = msg.get_payload(decode=True).decode()
    return from_email, body

def send_email_reply(to_email, body):
    """Отправка ответа на письмо"""
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = "Re: ваш запрос"
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = to_email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.send_message(msg)
        print(f"Ответ отправлен на {to_email}")

def main():
    from_email, body = fetch_latest_email()
    if not body:
        return
    print(f"Новое письмо от {from_email}:\n{body}")
    reply = generate_email_reply(body)
    print("\n--- Сгенерированный ответ ---\n", reply)
    send_email_reply(from_email, reply)

if __name__ == "__main__":
    main()