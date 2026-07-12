import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)

def send_contact_notification(sender_name: str, sender_email: str, subject: str, message_text: str):
    settings = get_settings()
    recipient = settings.contact_recipient_email

    # Styled HTML Email Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>New Portfolio Message</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #10131a;
                color: #e1e2ec;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #191b23;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            }}
            .header {{
                background: linear-gradient(135deg, #4d8eff, #d0bcff);
                padding: 35px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 800;
                color: #0b0e15;
                letter-spacing: -0.03em;
            }}
            .header p {{
                margin: 6px 0 0 0;
                font-size: 13px;
                color: #10131a;
                font-weight: 600;
                opacity: 0.85;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .field-group {{
                margin-bottom: 24px;
            }}
            .label {{
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: #adc6ff;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            .value {{
                font-size: 16px;
                color: #e1e2ec;
                line-height: 1.5;
            }}
            .value strong {{
                color: #ffffff;
            }}
            .message-box {{
                background-color: #1d2027;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-left: 4px solid #4d8eff;
                border-radius: 8px;
                padding: 22px;
                font-size: 15px;
                color: #e1e2ec;
                line-height: 1.6;
                white-space: pre-wrap;
                margin-top: 8px;
            }}
            .footer {{
                background-color: #0b0e15;
                padding: 30px;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .reply-btn {{
                display: inline-block;
                background-color: #4d8eff;
                color: #0b0e15 !important;
                text-decoration: none;
                font-weight: 700;
                font-size: 14px;
                padding: 14px 28px;
                border-radius: 8px;
                letter-spacing: -0.01em;
                box-shadow: 0 4px 14px rgba(77, 142, 255, 0.3);
            }}
            .reply-btn:hover {{
                background-color: #adc6ff;
            }}
            .footer-text {{
                font-size: 12px;
                color: #8c909f;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>New Message Received</h1>
                <p>Mufor Belmond Piannow Portfolio Contact Form</p>
            </div>
            <div class="content">
                <div class="field-group">
                    <div class="label">From</div>
                    <div class="value"><strong>{sender_name}</strong> &lt;{sender_email}&gt;</div>
                </div>
                <div class="field-group">
                    <div class="label">Subject</div>
                    <div class="value">{subject}</div>
                </div>
                <div class="field-group">
                    <div class="label">Message</div>
                    <div class="message-box">{message_text}</div>
                </div>
            </div>
            <div class="footer">
                <a href="mailto:{sender_email}" class="reply-btn">Reply to Sender</a>
                <div class="footer-text">
                    This notification was automatically sent from your Portfolio Backend.
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    recipients = [r.strip() for r in recipient.split(",") if r.strip()]

    # Print log showing the beautiful output
    logger.info(f"====== STYLED NOTIFICATION MAIL TRIGGERED FOR {', '.join(recipients)} ======")
    logger.info(f"From: {sender_name} <{sender_email}>")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body: {message_text}")
    logger.info("==================================================================")

    # Attempt SMTP transmission if host is configured
    if settings.smtp_host:
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_username and settings.smtp_password:
                    server.starttls()
                    server.login(settings.smtp_username, settings.smtp_password)
                
                for rec in recipients:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = f"[Portfolio Contact] {subject}"
                    msg["From"] = settings.smtp_from_email
                    msg["To"] = rec

                    part1 = MIMEText(f"New message from {sender_name} ({sender_email}):\n\n{message_text}", "plain")
                    part2 = MIMEText(html_content, "html")

                    msg.attach(part1)
                    msg.attach(part2)

                    server.sendmail(settings.smtp_from_email, rec, msg.as_string())
                    logger.info(f"Email successfully sent to {rec}")
        except Exception as e:
            logger.error(f"Failed to send styled notification email: {str(e)}")
    else:
        logger.info("No SMTP host configured. Logged notification email content above.")
