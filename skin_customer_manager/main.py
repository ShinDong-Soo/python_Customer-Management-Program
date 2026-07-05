from datetime import datetime

from database import (
    customer_has_visits,
    delete_customer as db_delete_customer,
    get_all_visits_with_customer,
    get_customer_by_id,
    get_visits_with_customer_by_id,
    initialize_database,
    insert_customer,
    insert_visit,
    load_customers,
    search_customers,
    update_customer as db_update_customer,
)


def require_customer(customer_id):
    customer_id = customer_id.strip()

    if not customer_id:
        print("고객 ID를 입력해주세요.")
        return None

    customer = get_customer_by_id(customer_id)

    if not customer:
        print("해당 ID의 고객을 찾을 수 없습니다.")
        return None

    return customer


def validate_date(date_str):
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return True, parsed.strftime("%Y-%m-%d")
    except ValueError:
        return False, None


def validate_price(price_str):
    if not price_str.isdigit():
        return False, None

    price = int(price_str)

    if price < 0:
        return False, None

    return True, str(price)


def add_customer():
    name = input("이름: ").strip()
    if not name:
        print("이름은 필수 입력입니다.")
        return

    phone = input("연락처: ").strip()
    if not phone:
        print("연락처는 필수 입력입니다.")
        return

    birth = input("생년월일: ")
    skin_type = input("피부 타입: ")
    memo = input("메모: ")

    insert_customer(
        name=name,
        phone=phone,
        birth=birth,
        skin_type=skin_type,
        memo=memo,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    print("고객이 등록되었습니다.")


def show_customers():
    customers = load_customers()

    if not customers:
        print("등록된 고객이 없습니다.")
        return

    print(f"\n총 고객 수 : {len(customers)}명\n")

    for customer in customers:
        print_customer(customer)


def search_customer():
    keyword = input("검색어 입력(이름 또는 연락처): ").strip()

    if not keyword:
        print("검색어를 입력해주세요.")
        return

    results = search_customers(keyword)

    if not results:
        print("검색 결과가 없습니다.")
        return

    for customer in results:
        print_customer(customer)


def update_customer():
    customer_id = input("수정할 고객 ID: ").strip()
    customer = require_customer(customer_id)

    if not customer:
        return

    print("수정하지 않을 항목은 Enter만 누르세요.")

    name = input(f"이름({customer['name']}): ")
    phone = input(f"연락처({customer['phone']}): ")
    birth = input(f"생년월일({customer['birth']}): ")
    skin_type = input(f"피부 타입({customer['skin_type']}): ")
    memo = input(f"메모({customer['memo']}): ")

    db_update_customer(
        customer_id=customer_id,
        name=name or customer["name"],
        phone=phone or customer["phone"],
        birth=birth or customer["birth"],
        skin_type=skin_type or customer["skin_type"],
        memo=memo or customer["memo"],
    )
    print("고객 정보가 수정되었습니다.")


def delete_customer():
    customer_id = input("삭제할 고객 ID: ").strip()
    customer = require_customer(customer_id)

    if not customer:
        return

    if customer_has_visits(customer_id):
        print("해당 고객은 방문 기록이 있어 삭제할 수 없습니다.")
        print("방문 기록을 먼저 삭제한 후 다시 시도해주세요.")
        return

    confirm = input("정말 삭제하시겠습니까? (Y/N): ")

    if confirm.upper() != "Y":
        print("삭제가 취소되었습니다.")
        return

    db_delete_customer(customer_id)
    print("고객 정보가 삭제되었습니다.")


def add_visit():
    customer_id = input("고객 ID: ").strip()
    customer = require_customer(customer_id)

    if not customer:
        return

    date = input("방문 날짜 (YYYY-MM-DD): ").strip()
    is_valid_date, normalized_date = validate_date(date)

    if not is_valid_date:
        print("방문 날짜는 YYYY-MM-DD 형식으로 입력해주세요. (예: 2025-03-12)")
        return

    service = input("시술 내용: ").strip()
    if not service:
        print("시술 내용은 필수 입력입니다.")
        return

    price = input("가격: ").strip()
    is_valid_price, normalized_price = validate_price(price)

    if not is_valid_price:
        print("가격은 0 이상의 숫자로 입력해주세요.")
        return

    memo = input("메모: ")

    insert_visit(
        customer_id=customer_id,
        date=normalized_date,
        service=service,
        price=normalized_price,
        memo=memo,
    )

    print("방문 기록이 등록되었습니다.")


def show_customer_visits():
    customer_id = input("고객 ID: ").strip()

    if not customer_id:
        print("고객 ID를 입력해주세요.")
        return

    customer, customer_visits = get_visits_with_customer_by_id(customer_id)

    if not customer:
        print("해당 ID의 고객을 찾을 수 없습니다.")
        return

    if not customer_visits:
        print("등록된 방문 기록이 없습니다.")
        return

    print(f"\n[{customer['name']}] 방문 기록 (JOIN 조회)\n")

    for visit in customer_visits:
        print_visit(visit)

    print(f"\n총 방문 횟수 : {len(customer_visits)}회\n")


def show_all_visits_with_customer():
    visits = get_all_visits_with_customer()

    if not visits:
        print("등록된 방문 기록이 없습니다.")
        return

    print(f"\n전체 방문 기록 (JOIN 조회) — 총 {len(visits)}건\n")

    for visit in visits:
        print_visit_with_customer(visit)


def print_visit_with_customer(visit):
    print("-" * 40)
    print(f"고객: {visit['customer_name']} (ID: {visit['customer_id']})")
    print(f"방문 ID: {visit['visit_id']}")
    print(f"방문 날짜: {visit['date']}")
    print(f"시술 내용: {visit['service']}")
    print(f"가격: {visit['price']}")
    print(f"메모: {visit['memo']}")


def show_menu():
    print("\n=== 피부관리샵 고객 관리 프로그램 ===")
    print("1. 고객 등록")
    print("2. 고객 목록 조회")
    print("3. 고객 검색")
    print("4. 고객 정보 수정")
    print("5. 고객 삭제")
    print("6. 방문 기록 등록")
    print("7. 고객별 방문 기록 조회")
    print("8. 전체 방문 기록 조회 (JOIN)")
    print("0. 종료")


def print_customer(customer):
    print("-" * 40)
    print(f"ID: {customer['id']}")
    print(f"이름: {customer['name']}")
    print(f"연락처: {customer['phone']}")
    print(f"생년월일: {customer['birth']}")
    print(f"피부 타입: {customer['skin_type']}")
    print(f"메모: {customer['memo']}")
    print(f"등록일: {customer.get('created_at', '')}")


def print_visit(visit):
    print("-" * 40)
    print(f"방문 ID: {visit['visit_id']}")
    print(f"방문 날짜: {visit['date']}")
    print(f"시술 내용: {visit['service']}")
    print(f"가격: {visit['price']}")
    print(f"메모: {visit['memo']}")


def main():
    initialize_database()

    while True:
        show_menu()
        choice = input("메뉴 선택: ")

        if choice == "1":
            add_customer()
        elif choice == "2":
            show_customers()
        elif choice == "3":
            search_customer()
        elif choice == "4":
            update_customer()
        elif choice == "5":
            delete_customer()
        elif choice == "6":
            add_visit()
        elif choice == "7":
            show_customer_visits()
        elif choice == "8":
            show_all_visits_with_customer()
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 메뉴입니다.")


if __name__ == "__main__":
    main()
