from __future__ import annotations

from dataclasses import dataclass
import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(slots=True)
class NotificationResult:
    channel: str
    status: str
    detail: str


def send_notification(subject: str, markdown: str, channels: str | None = None) -> list[NotificationResult]:
    selected = channels or os.getenv("RESEARCH_NOTIFY_CHANNELS", "")
    results = []
    for channel in [item.strip().lower() for item in selected.split(",") if item.strip()]:
        if channel == "email":
            results.append(_send_email(subject, markdown))
        elif channel in {"serverchan", "serverchan-turbo", "sct"}:
            results.append(_send_serverchan(subject, markdown))
        elif channel == "wxpusher":
            results.append(_send_wxpusher(subject, markdown))
        else:
            results.append(NotificationResult(channel=channel, status="skipped", detail="unknown channel"))
    return results


def _send_email(subject: str, markdown: str) -> NotificationResult:
    host = os.getenv("RESEARCH_SMTP_HOST", "")
    username = os.getenv("RESEARCH_SMTP_USERNAME", "")
    password = os.getenv("RESEARCH_SMTP_PASSWORD", "")
    sender = os.getenv("RESEARCH_SMTP_FROM", username)
    recipients = [item.strip() for item in os.getenv("RESEARCH_EMAIL_TO", "").split(",") if item.strip()]
    port = int(os.getenv("RESEARCH_SMTP_PORT", "465"))
    if not host or not sender or not recipients:
        return NotificationResult("email", "skipped", "missing email settings")
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(markdown)
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=20) as smtp:
        if username or password:
            smtp.login(username, password)
        smtp.send_message(message)
    return NotificationResult("email", "sent", f"sent to {len(recipients)} recipient(s)")


def _send_serverchan(subject: str, markdown: str) -> NotificationResult:
    sendkey = os.getenv("RESEARCH_SERVERCHAN_SENDKEY", "").strip()
    if not sendkey:
        return NotificationResult("serverchan", "skipped", "missing sendkey")
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    payload = urlencode({"title": subject[:80], "desp": markdown}).encode("utf-8")
    raw = _post(url, payload, "application/x-www-form-urlencoded")
    return NotificationResult("serverchan", "sent", raw[:200])


def _send_wxpusher(subject: str, markdown: str) -> NotificationResult:
    spt = os.getenv("RESEARCH_WXPUSHER_SPT", "").strip()
    app_token = os.getenv("RESEARCH_WXPUSHER_APP_TOKEN", "").strip()
    if spt:
        url = "https://wxpusher.zjiecode.com/api/send/message"
        payload = json.dumps({"spt": spt, "content": f"{subject}\n\n{markdown}"}).encode("utf-8")
        raw = _post(url, payload, "application/json")
        return NotificationResult("wxpusher", "sent", raw[:200])
    if app_token:
        uids = [item.strip() for item in os.getenv("RESEARCH_WXPUSHER_UIDS", "").split(",") if item.strip()]
        url = "https://wxpusher.zjiecode.com/api/send/message"
        payload = json.dumps(
            {
                "appToken": app_token,
                "content": f"{subject}\n\n{markdown}",
                "contentType": 1,
                "uids": uids,
            }
        ).encode("utf-8")
        raw = _post(url, payload, "application/json")
        return NotificationResult("wxpusher", "sent", raw[:200])
    return NotificationResult("wxpusher", "skipped", "missing wxpusher token")


def _post(url: str, payload: bytes, content_type: str) -> str:
    request = Request(url, data=payload, headers={"Content-Type": content_type}, method="POST")
    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"notification request failed: {exc}") from exc
