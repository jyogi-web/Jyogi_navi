import re

# メールアドレス
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# 日本の電話番号 (ハイフンあり・なし、国際形式含む)
_PHONE_RE = re.compile(r"(?:\+81[-\s]?|0)(?:\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4})")

# 郵便番号 (〒マークあり・なし、ハイフンあり・なし)
_ZIPCODE_RE = re.compile(r"(?<!\d)〒?\d{3}[-ー]?\d{4}(?!\d)")


def mask(text: str) -> str:
    """テキスト内の PII を正規表現でマスキングして返す。"""
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _PHONE_RE.sub("[PHONE]", text)
    text = _ZIPCODE_RE.sub("[ZIPCODE]", text)
    return text
