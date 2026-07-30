"""
Celery tasks for Afrikbook — primarily async email delivery.

Tasks must only receive JSON-serializable arguments (no request objects).
Multi-tenant DBs are registered on the worker the same way middleware does.
"""
from __future__ import annotations

import base64
import logging
import os
import traceback

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.db import connections

logger = logging.getLogger(__name__)


def _from_email():
    return getattr(settings, "DEFAULT_FROM_EMAIL", None) or settings.EMAIL_HOST_USER


def ensure_tenant_db(db_name: str) -> str:
    """Register a company database connection on this worker process if needed."""
    if not db_name:
        return "default"
    if db_name in connections.databases:
        return db_name

    config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": "5432",
        "TIME_ZONE": "UTC",
        "OPTIONS": {"options": "-c timezone=UTC"},
        "CONN_HEALTH_CHECKS": False,
        "CONN_MAX_AGE": 0,
        "AUTOCOMMIT": True,
        "ATOMIC_REQUESTS": False,
    }
    connections.databases[db_name] = config
    settings.DATABASES[db_name] = config
    logger.info("[celery] Registered tenant DB %s", db_name)
    return db_name


@shared_task(
    bind=True,
    name="main.tasks.send_email_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_email_task(self, recipients, subject, message, html_message=None):
    """
    Send a plain / HTML email asynchronously.

    recipients: list of email addresses
    """
    if isinstance(recipients, str):
        recipients = [recipients]
    try:
        result = send_mail(
            subject,
            message,
            _from_email(),
            recipients,
            fail_silently=False,
            html_message=html_message or message,
        )
        logger.info(
            "[send_email_task] OK | to=%s | subject=%s | result=%s",
            recipients,
            subject,
            result,
        )
        return {"ok": True, "result": result}
    except Exception as exc:
        logger.error(
            "[send_email_task] FAILED | to=%s | %s\n%s",
            recipients,
            exc,
            traceback.format_exc(),
        )
        raise


@shared_task(
    bind=True,
    name="main.tasks.send_email_with_attachment_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_email_with_attachment_task(
    self,
    recipients,
    subject,
    body,
    attachment_filename,
    attachment_b64,
    attachment_mimetype="application/pdf",
):
    """
    Send an email with a binary attachment (base64-encoded for the broker).
    """
    if isinstance(recipients, str):
        recipients = [recipients]
    try:
        payload = base64.b64decode(attachment_b64)
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=_from_email(),
            to=recipients,
        )
        email.attach(attachment_filename, payload, attachment_mimetype)
        email.send(fail_silently=False)
        logger.info(
            "[send_email_with_attachment_task] OK | to=%s | file=%s",
            recipients,
            attachment_filename,
        )
        return {"ok": True}
    except Exception as exc:
        logger.error(
            "[send_email_with_attachment_task] FAILED | to=%s | %s\n%s",
            recipients,
            exc,
            traceback.format_exc(),
        )
        raise


@shared_task(
    bind=True,
    name="main.tasks.send_invoice_email_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_invoice_email_task(
    self,
    db_name,
    invoice_id,
    customer_email,
    customer_name,
    company_display_name="",
    base_url="",
):
    """
    Build sales invoice PDF and email it (runs off the request thread).

    Called when a new sales invoice is created and profile.send_email_invoice is on.
    """
    from django.template.loader import render_to_string
    from weasyprint import HTML

    from customer.models import Vat, customer_invoice
    from settings.models import CreateProfile

    db = ensure_tenant_db(db_name)
    try:
        invoice_items = customer_invoice.objects.using(db).filter(invoiceID=invoice_id)
        if not invoice_items.exists():
            logger.error(
                "[send_invoice_email_task] Invoice not found | db=%s | invoice=%s",
                db,
                invoice_id,
            )
            return {"ok": False, "error": "Invoice not found"}

        invoice = invoice_items.first()
        company = CreateProfile.objects.using(db).first()

        subtotal = sum(item.amount for item in invoice_items)
        vat_items = Vat.objects.using(db).filter(source=invoice_id)
        vat_total = sum(v.amount for v in vat_items)
        grand_total = subtotal + vat_total
        balance_due = grand_total - (invoice.amount_paid or 0)

        company_name = (
            (company.CompanyName if company and company.CompanyName else None)
            or company_display_name
            or "Afrikbook"
        )
        company_address = company.address if company and company.address else ""
        company_email = company.email if company and company.email else ""
        company_rc = company.Rc if company and company.Rc else ""

        html_content = render_to_string(
            "customer/invoice_pdf.html",
            {
                "invoice": invoice,
                "invoice_items": invoice_items,
                "company": company,
                "subtotal": subtotal,
                "vat_items": vat_items,
                "vat_total": vat_total,
                "grand_total": grand_total,
                "balance_due": balance_due,
            },
        )

        pdf_base = base_url or getattr(settings, "SITE_URL", "https://console.afrikbook.com")
        pdf_file = HTML(string=html_content, base_url=pdf_base).write_pdf()

        footer_lines = [company_name]
        if company_address:
            footer_lines.append(company_address)
        if company_email:
            footer_lines.append(company_email)
        if company_rc:
            footer_lines.append(f"RC {company_rc}")
        footer = "\n".join(footer_lines)

        email = EmailMessage(
            subject=f"Invoice {invoice_id} from {company_name}",
            body=(
                f"Dear {customer_name},\n\n"
                f"Here is your invoice {invoice_id}. We appreciate your business!\n"
                f"Please find the attached document for your invoice details.\n"
                f"──────────────────────────\n"
                f"{footer}\n"
                f"──────────────────────────"
            ),
            from_email=_from_email(),
            to=[customer_email],
        )
        email.attach(f"Invoice_{invoice_id}.pdf", pdf_file, "application/pdf")
        email.send(fail_silently=False)

        logger.info(
            "[send_invoice_email_task] Sent | invoice=%s | to=%s",
            invoice_id,
            customer_email,
        )
        return {"ok": True}
    except Exception as exc:
        logger.error(
            "[send_invoice_email_task] FAILED | invoice=%s | %s\n%s",
            invoice_id,
            exc,
            traceback.format_exc(),
        )
        raise


@shared_task(
    bind=True,
    name="main.tasks.send_receipt_email_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_receipt_email_task(
    self,
    db_name,
    customer_email,
    customer_name,
    invoice_no,
    customer_code,
    date_str,
    amount,
    amount_in_words,
    description,
    payment_method,
    company_display_name="",
    base_url="",
):
    """Email payment receipt PDF after receive-payment (async)."""
    from django.template.loader import render_to_string
    from weasyprint import HTML

    from settings.models import CreateProfile

    db = ensure_tenant_db(db_name)
    try:
        company = CreateProfile.objects.using(db).first()
        company_name = (
            (company.CompanyName if company and company.CompanyName else None)
            or company_display_name
            or "Afrikbook"
        )
        company_address = company.address if company and company.address else ""
        company_email_ = company.email if company and company.email else ""
        company_phone = company.phone if company and company.phone else ""
        company_rc = company.Rc if company and company.Rc else ""

        html_content = render_to_string(
            "journal/receipt_email.html",
            {
                "company": company,
                "customer_name": customer_name,
                "invoice_no": invoice_no,
                "customer_code": customer_code,
                "date": date_str,
                "amount": amount,
                "amount_in_words": amount_in_words,
                "description": description,
                "payment_method": payment_method,
            },
        )
        pdf_base = base_url or getattr(settings, "SITE_URL", "https://console.afrikbook.com")
        pdf_file = HTML(string=html_content, base_url=pdf_base).write_pdf()

        footer_lines = [company_name]
        if company_address:
            footer_lines.append(company_address)
        if company_email_:
            footer_lines.append(company_email_)
        if company_phone:
            footer_lines.append(company_phone)
        if company_rc:
            footer_lines.append(f"RC {company_rc}")

        email = EmailMessage(
            subject=f"Payment Receipt — Invoice {invoice_no}",
            body=(
                f"Dear {customer_name},\n\n"
                f"Thank you for your payment of {amount} for invoice {invoice_no}.\n"
                f"Please find your receipt attached.\n\n"
                f"──────────────────────────\n"
                f"{chr(10).join(footer_lines)}\n"
                f"──────────────────────────"
            ),
            from_email=_from_email(),
            to=[customer_email],
        )
        email.attach(f"Receipt_{invoice_no}.pdf", pdf_file, "application/pdf")
        email.send(fail_silently=False)

        logger.info(
            "[send_receipt_email_task] Sent | invoice=%s | to=%s",
            invoice_no,
            customer_email,
        )
        return {"ok": True}
    except Exception as exc:
        logger.error(
            "[send_receipt_email_task] FAILED | invoice=%s | %s\n%s",
            invoice_no,
            exc,
            traceback.format_exc(),
        )
        raise
