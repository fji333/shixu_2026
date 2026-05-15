import re


PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")
ID_CARD_RE = re.compile(r"(?<!\d)(\d{17}[\dXx])(?!\d)")
BANK_CARD_RE = re.compile(r"(?<!\d)(\d{16,19})(?!\d)")
EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")
ADDRESS_KEYWORDS = ["省", "市", "区", "县", "街道", "小区", "栋", "单元", "号", "路", "镇", "村"]


def _has_possible_address(text: str) -> bool:
    keyword_count = sum(1 for keyword in ADDRESS_KEYWORDS if keyword in text)
    return len(text) >= 18 and keyword_count >= 2


def _append_detection(
    types: list[str],
    warnings: list[str],
    sensitive_type: str,
    warning: str,
) -> None:
    if sensitive_type not in types:
        types.append(sensitive_type)
        warnings.append(warning)


def detect_sensitive_info(text: str) -> dict:
    types: list[str] = []
    warnings: list[str] = []

    if PHONE_RE.search(text):
        _append_detection(types, warnings, "phone", "检测到手机号")
    if ID_CARD_RE.search(text):
        _append_detection(types, warnings, "id_card", "检测到身份证号")
    if EMAIL_RE.search(text):
        _append_detection(types, warnings, "email", "检测到邮箱")

    id_spans = [match.span() for match in ID_CARD_RE.finditer(text)]
    for match in BANK_CARD_RE.finditer(text):
        start, end = match.span()
        overlaps_id = any(start < id_end and end > id_start for id_start, id_end in id_spans)
        if not overlaps_id:
            _append_detection(types, warnings, "bank_card", "检测到银行卡号")
            break

    if _has_possible_address(text):
        _append_detection(types, warnings, "address", "检测到可能的详细住址")

    return {
        "has_sensitive_info": bool(types),
        "types": types,
        "warnings": warnings,
    }


def _mask_phone(match: re.Match) -> str:
    value = match.group(1)
    return f"{value[:3]}****{value[-4:]}"


def _mask_id_card(match: re.Match) -> str:
    value = match.group(1)
    return f"{value[:3]}{'*' * (len(value) - 7)}{value[-4:]}"


def _mask_bank_card(match: re.Match) -> str:
    value = match.group(1)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def _mask_email(match: re.Match) -> str:
    value = match.group(1)
    local_part, domain = value.split("@", 1)
    prefix = local_part[:1] if local_part else "*"
    return f"{prefix}***@{domain}"


def mask_sensitive_info(text: str) -> str:
    masked = EMAIL_RE.sub(_mask_email, text)
    masked = ID_CARD_RE.sub(_mask_id_card, masked)
    masked = PHONE_RE.sub(_mask_phone, masked)
    masked = BANK_CARD_RE.sub(_mask_bank_card, masked)
    return masked


def build_safety_warning(result: dict) -> str | None:
    if not result.get("has_sensitive_info"):
        return None

    return (
        "系统检测到您输入中可能包含个人敏感信息，已进行脱敏处理。"
        "请勿在咨询中提交完整身份证号、银行卡号、手机号、家庭住址等信息。"
    )
