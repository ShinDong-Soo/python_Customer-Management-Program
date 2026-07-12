from dataclasses import dataclass

from database import customer_has_visits, get_customer_by_id, get_customer_by_phone
from validators import validate_date, validate_price


@dataclass
class ServiceResult:
    ok: bool
    data: dict | None = None
    message: str = ""


def prepare_customer_data(
    name,
    phone,
    birth="",
    skin_type="",
    memo="",
    exclude_customer_id=None,
):
    name = (name or "").strip()
    phone = (phone or "").strip()

    if not name:
        return ServiceResult(False, message="이름은 필수 입력입니다.")

    if not phone:
        return ServiceResult(False, message="연락처는 필수 입력입니다.")

    existing = get_customer_by_phone(phone, exclude_customer_id=exclude_customer_id)
    if existing:
        return ServiceResult(
            False,
            message=(
                f"이미 등록된 연락처입니다.\n"
                f"기존 고객: {existing['name']} (ID: {existing['id']})"
            ),
        )

    return ServiceResult(
        True,
        data={
            "name": name,
            "phone": phone,
            "birth": (birth or "").strip(),
            "skin_type": (skin_type or "").strip(),
            "memo": (memo or "").strip(),
        },
    )


def prepare_visit_data(customer_id, date, service, price, memo):
    customer_id = str(customer_id or "").strip()
    if not customer_id or not customer_id.isdigit():
        return ServiceResult(False, message="고객을 선택해주세요.")

    customer = get_customer_by_id(customer_id)
    if not customer:
        return ServiceResult(False, message="해당 고객을 찾을 수 없습니다.")

    date = (date or "").strip()
    is_valid_date, normalized_date = validate_date(date)
    if not is_valid_date:
        return ServiceResult(
            False,
            message="방문 날짜는 YYYY-MM-DD 형식으로 입력해주세요.\n(예: 2025-03-12)",
        )

    service = (service or "").strip()
    if not service:
        return ServiceResult(False, message="시술 내용은 필수 입력입니다.")

    price = (price or "").strip()
    is_valid_price, normalized_price = validate_price(price)
    if not is_valid_price:
        return ServiceResult(False, message="가격은 0 이상의 숫자로 입력해주세요.")

    return ServiceResult(
        True,
        data={
            "customer_id": customer_id,
            "date": normalized_date,
            "service": service,
            "price": normalized_price,
            "memo": (memo or "").strip(),
        },
    )


def check_customer_deletable(customer_id):
    customer_id = str(customer_id or "").strip()
    if not customer_id:
        return ServiceResult(False, message="삭제할 고객을 선택해주세요.")

    customer = get_customer_by_id(customer_id)
    if not customer:
        return ServiceResult(False, message="해당 고객을 찾을 수 없습니다.")

    if customer_has_visits(customer_id):
        return ServiceResult(
            False,
            message=(
                "해당 고객은 방문 기록이 있어 삭제할 수 없습니다.\n"
                "방문 기록을 먼저 삭제한 후 다시 시도해주세요."
            ),
        )

    return ServiceResult(True, data=customer)


def check_customer_updatable(customer_id):
    customer_id = str(customer_id or "").strip()
    if not customer_id:
        return ServiceResult(False, message="수정할 고객을 목록에서 선택해주세요.")

    customer = get_customer_by_id(customer_id)
    if not customer:
        return ServiceResult(False, message="해당 고객을 찾을 수 없습니다.")

    return ServiceResult(True, data=customer)


def check_visit_updatable(visit_id):
    visit_id = str(visit_id or "").strip()
    if not visit_id:
        return ServiceResult(False, message="수정할 방문 기록을 목록에서 선택해주세요.")

    from database import get_visit_by_id

    visit = get_visit_by_id(visit_id)
    if not visit:
        return ServiceResult(False, message="해당 방문 기록을 찾을 수 없습니다.")

    return ServiceResult(True, data=visit)


def check_visit_deletable(visit_id):
    visit_id = str(visit_id or "").strip()
    if not visit_id:
        return ServiceResult(False, message="삭제할 방문 기록을 목록에서 선택해주세요.")

    from database import get_visit_by_id

    visit = get_visit_by_id(visit_id)
    if not visit:
        return ServiceResult(False, message="해당 방문 기록을 찾을 수 없습니다.")

    return ServiceResult(True, data=visit)
