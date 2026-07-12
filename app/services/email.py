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
        <title>New Portfolio message</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #0b0f19;
                color: #f3f4f6;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }}
            .header {{
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                padding: 30px;
                text-align: center;
                border-bottom: 1px solid #1f2937;
            }}
            .header h1 {{
                margin: 0;
                font-size: 22px;
                font-weight: 700;
                color: #ffffff;
                letter-spacing: -0.025em;
            }}
            .header p {{
                margin: 5px 0 0 0;
                font-size: 14px;
                color: #bfdbfe;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .field-group {{
                margin-bottom: 24px;
                border-bottom: 1px solid #1f2937;
                padding-bottom: 16px;
            }}
            .field-group:last-of-type {{
                border-bottom: none;
                padding-bottom: 0;
            }}
            .label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #9ca3af;
                font-weight: 600;
                margin-bottom: 6px;
            }}
            .value {{
                font-size: 16px;
                color: #f3f4f6;
                line-height: 1.5;
            }}
            .message-box {{
                background-color: #1f2937;
                border-left: 4px solid #3b82f6;
                border-radius: 8px;
                padding: 20px;
                font-size: 15px;
                color: #e5e7eb;
                line-height: 1.6;
                white-space: pre-wrap;
                margin-top: 10px;
            }}
            .footer {{
                background-color: #0b0f19;
                padding: 20px 30px;
                text-align: center;
                border-top: 1px solid #1f2937;
            }}
            .reply-btn {{
                display: inline-block;
                background-color: #3b82f6;
                color: #ffffff !important;
                text-decoration: none;
                font-weight: 700;
                font-size: 14px;
                padding: 12px 24px;
                border-radius: 8px;
                margin-top: 10px;
                transition: background-color 150ms ease;
            }}
            .reply-btn:hover {{
                background-color: #2563eb;
            }}
            .footer-text {{
                font-size: 12px;
                color: #6b7280;
                margin-top: 15px;
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
