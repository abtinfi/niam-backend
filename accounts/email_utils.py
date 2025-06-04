# accounts/email_utils.py
import resend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(to_email: str, otp_code: str, username: str, purpose: str = 'email_verification'):
    if not settings.RESEND_API_KEY:
        logger.error("RESEND_API_KEY is not configured.")
        return False
    if not settings.DEFAULT_FROM_EMAIL_RESEND:
        logger.error("DEFAULT_FROM_EMAIL_RESEND is not configured.")
        return False

    resend.api_key = settings.RESEND_API_KEY

    if purpose == 'email_verification':
        subject = "کد فعال‌سازی حساب کاربری شما"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; text-align: right;">
            <p>سلام {username}،</p>
            <p>از اینکه در سامانه ما ثبت‌نام کردید متشکریم. کد فعال‌سازی حساب شما:</p>
            <p style="font-size: 24px; font-weight: bold; letter-spacing: 2px;">{otp_code}</p>
            <p>این کد به مدت 10 دقیقه معتبر است.</p>
            <p>لطفاً برای فعال‌سازی حساب خود از این کد استفاده کنید.</p>
            <p>با تشکر.</p>
        </div>
        """
    elif purpose == 'password_reset':
        subject = "کد تایید بازنشانی رمز عبور شما"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; text-align: right;">
            <p>سلام {username}،</p>
            <p>شما درخواست بازنشانی رمز عبور خود را داده‌اید. کد تایید شما:</p>
            <p style="font-size: 24px; font-weight: bold; letter-spacing: 2px;">{otp_code}</p>
            <p>این کد به مدت 5 دقیقه معتبر است.</p> <p>اگر شما این درخواست را نداده‌اید، این ایمیل را نادیده بگیرید.</p>
            <p>با تشکر.</p>
        </div>
        """
    else:
        logger.warning(f"Unknown OTP purpose: {purpose}")
        return False

    params = {
        "from": settings.DEFAULT_FROM_EMAIL_RESEND,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    try:
        email_response = resend.Emails.send(params)
        if email_response.get("id"):
            logger.info(f"OTP email ({purpose}) sent successfully to {to_email}. Email ID: {email_response.get('id')}")
            return True
        else:
            logger.error(f"Failed to send OTP email ({purpose}) to {to_email}. Response: {email_response}")
            return False
    except Exception as e:
        logger.error(f"Exception during sending OTP email ({purpose}) to {to_email}: {e}")
        return False