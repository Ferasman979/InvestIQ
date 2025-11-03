"""
Email Service
Handles sending emails for transaction verification and notifications
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from models.Transcation import TransactionDB
from logging_utils import get_logger

LOGGER = get_logger("guardian")


def send_verification_email(
    user_email: str,
    transaction: TransactionDB,
    reason: str,
    verification_url: str
) -> bool:
    """
    Send verification email to user about suspicious transaction.
    Returns True if sent successfully, False otherwise.
    """
    try:
        # Get SMTP configuration from environment
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        email_from = os.getenv("EMAIL_FROM", smtp_username)
        
        if not smtp_username or not smtp_password:
            LOGGER.warning("SMTP credentials not configured, skipping email")
            return False
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Transaction Verification Required - ${transaction.amount}"
        msg["From"] = email_from
        msg["To"] = user_email
        
        # Email body
        html_body = f"""
        <html>
          <body>
            <h2>Transaction Verification Required</h2>
            <p>Hello,</p>
            <p>We detected a suspicious transaction on your account that requires verification:</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Transaction ID:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{transaction.id}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Amount:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">${transaction.amount}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Vendor:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{transaction.vendor}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Category:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{transaction.category}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Date:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{transaction.tx_date}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Reason:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{reason}</td>
              </tr>
            </table>
            <p style="margin-top: 20px;">
              <strong>The transaction has been temporarily locked.</strong>
            </p>
            <p>Please verify this transaction by answering your security questions:</p>
            <p>
              <a href="{verification_url}" 
                 style="background-color: #4CAF50; color: white; padding: 14px 20px; 
                        text-decoration: none; display: inline-block; border-radius: 4px;">
                Verify Transaction
              </a>
            </p>
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
              If you did not make this transaction, please contact support immediately.
            </p>
          </body>
        </html>
        """
        
        text_body = f"""
        Transaction Verification Required
        
        We detected a suspicious transaction on your account:
        
        Transaction ID: {transaction.id}
        Amount: ${transaction.amount}
        Vendor: {transaction.vendor}
        Category: {transaction.category}
        Date: {transaction.tx_date}
        Reason: {reason}
        
        The transaction has been temporarily locked.
        
        Please verify this transaction by visiting:
        {verification_url}
        
        If you did not make this transaction, please contact support immediately.
        """
        
        # Attach both plain text and HTML
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        LOGGER.info(f"Verification email sent to {user_email} for transaction {transaction.id}")
        return True
        
    except Exception as e:
        LOGGER.error(f"Failed to send verification email: {e}")
        return False


def send_approval_email(
    user_email: str,
    transaction: TransactionDB,
    provider_ref: Optional[str] = None
) -> bool:
    """
    Send confirmation email when transaction is approved and sent to vendor.
    """
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        email_from = os.getenv("EMAIL_FROM", smtp_username)
        
        if not smtp_username or not smtp_password:
            return False
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Transaction Approved - ${transaction.amount} to {transaction.vendor}"
        msg["From"] = email_from
        msg["To"] = user_email
        
        html_body = f"""
        <html>
          <body>
            <h2>Transaction Approved</h2>
            <p>Hello,</p>
            <p>Your transaction has been verified and approved:</p>
            <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Transaction ID:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{transaction.id}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Amount:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">${transaction.amount}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Vendor:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{transaction.vendor}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Completed</td>
              </tr>
            </table>
            <p style="margin-top: 20px;">
              The payment has been sent to the vendor successfully.
            </p>
        """
        
        if provider_ref:
            html_body += f'<p><strong>Payment Reference:</strong> {provider_ref}</p>'
        
        html_body += """
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        LOGGER.info(f"Approval email sent to {user_email} for transaction {transaction.id}")
        return True
        
    except Exception as e:
        LOGGER.error(f"Failed to send approval email: {e}")
        return False

