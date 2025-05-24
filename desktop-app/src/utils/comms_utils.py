import smtplib
from email.mime.text import MIMEText



def generate_plaintext_day_report(self, child_name, entry, include_starter=False):
    lines = [
        f"Child: {child_name}",
        f"Arrival: {entry.get('arrival', '-')}",
        f"Departure: {entry.get('departure', '-')}"
    ]
    if include_starter:
        starter_raw = entry.get("starter")
        starter = self.slider_word_map.get(int(starter_raw), "-") if starter_raw is not None else "-"
        lines.append(f"Starter: {starter}")

    main_raw = entry.get("main")
    main = self.slider_word_map.get(int(main_raw), "-") if main_raw is not None else "-"
    dessert_raw = entry.get("dessert")
    dessert = self.slider_word_map.get(int(dessert_raw), "-") if dessert_raw is not None else "-"

    lines.extend([
        f"Main: {main}",
        f"Dessert: {dessert}",
        f"Sleep: {entry.get('sleep', '-')}",
        f"Poops: {entry.get('poop_count', 0)}",
        f"Comments: {entry.get('comments', '')}"
    ])
    return "\n".join(lines)

def send_email(to_email, subject, body):
    from_email = "kieranglass23@gmail.com"
    password = "opma lnkh vfwy hydh" 

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.send_message(msg)

