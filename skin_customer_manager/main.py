import csv
import os
from datetime import datetime


CUSTOMERS_FILE = "customers.csv"
VISITS_FILE = "visits.csv"

CUSTOMER_FIELDS = [
    "id",
    "name",
    "phone",
    "birth",
    "skin_type",
    "memo",
    "created_at",
]

VISIT_FIELDS = [
    "visit_id",
    "customer_id",
    "date",
    "service",
    "price",
    "memo",
]


def initialize_csv():
    if not os.path.exists(CUSTOMERS_FILE):
        with open(CUSTOMERS_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=CUSTOMER_FIELDS)
            writer.writeheader()

    if not os.path.exists(VISITS_FILE):
        with open(VISITS_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=VISIT_FIELDS)
            writer.writeheader()


def load_customers():
    customers = []

    with open(CUSTOMERS_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            customers.append(row)

    return customers


def save_customers(customers):
    with open(CUSTOMERS_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CUSTOMER_FIELDS)
        writer.writeheader()
        writer.writerows(customers)


def load_visits():
    visits = []

    with open(VISITS_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            visits.append(row)

    return visits


def save_visits(visits):
    with open(VISITS_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=VISIT_FIELDS)
        writer.writeheader()
        writer.writerows(visits)


def get_next_id(customers):
    if not customers:
        return 1

    max_id = max(int(customer["id"]) for customer in customers)
    return max_id + 1


def get_next_visit_id(visits):
    if not visits:
        return 1

    max_id = max(int(visit["visit_id"]) for visit in visits)
    return max_id + 1


def find_customer(customers, customer_id):
    for customer in customers:
        if customer["id"] == customer_id:
            return customer
    return None


def require_customer(customers, customer_id):
    customer_id = customer_id.strip()

    if not customer_id:
        print("고객 ID를 입력해주세요.")
        return None

    customer = find_customer(customers, customer_id)

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


def has_customer_visits(visits, customer_id):
    return any(visit["customer_id"] == customer_id for visit in visits)


def add_customer():
    customers = load_customers()

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

    customer = {
        "id": str(get_next_id(customers)),
        "name": name,
        "phone": phone,
        "birth": birth,
        "skin_type": skin_type,
        "memo": memo,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    customers.append(customer)
    save_customers(customers)

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
    customers = load_customers()
    keyword = input("검색어 입력(이름 또는 연락처): ")

    results = [
        customer
        for customer in customers
        if keyword in customer["name"] or keyword in customer["phone"]
    ]

    if not results:
        print("검색 결과가 없습니다.")
        return

    for customer in results:
        print_customer(customer)


def update_customer():
    customers = load_customers()
    customer_id = input("수정할 고객 ID: ").strip()
    customer = require_customer(customers, customer_id)

    if not customer:
        return

    print("수정하지 않을 항목은 Enter만 누르세요.")

    name = input(f"이름({customer['name']}): ")
    phone = input(f"연락처({customer['phone']}): ")
    birth = input(f"생년월일({customer['birth']}): ")
    skin_type = input(f"피부 타입({customer['skin_type']}): ")
    memo = input(f"메모({customer['memo']}): ")

    if name:
        customer["name"] = name
    if phone:
        customer["phone"] = phone
    if birth:
        customer["birth"] = birth
    if skin_type:
        customer["skin_type"] = skin_type
    if memo:
        customer["memo"] = memo

    save_customers(customers)
    print("고객 정보가 수정되었습니다.")


def delete_customer():
    customers = load_customers()
    visits = load_visits()
    customer_id = input("삭제할 고객 ID: ").strip()
    customer = require_customer(customers, customer_id)

    if not customer:
        return

    if has_customer_visits(visits, customer_id):
        print("해당 고객은 방문 기록이 있어 삭제할 수 없습니다.")
        print("방문 기록을 먼저 삭제한 후 다시 시도해주세요.")
        return

    confirm = input("정말 삭제하시겠습니까? (Y/N): ")

    if confirm.upper() != "Y":
        print("삭제가 취소되었습니다.")
        return

    new_customers = [
        c for c in customers if c["id"] != customer_id
    ]
    save_customers(new_customers)
    print("고객 정보가 삭제되었습니다.")


def add_visit():
    customers = load_customers()
    visits = load_visits()

    customer_id = input("고객 ID: ").strip()
    customer = require_customer(customers, customer_id)

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

    visit = {
        "visit_id": str(get_next_visit_id(visits)),
        "customer_id": customer_id,
        "date": normalized_date,
        "service": service,
        "price": normalized_price,
        "memo": memo,
    }

    visits.append(visit)
    save_visits(visits)

    print("방문 기록이 등록되었습니다.")


def show_customer_visits():
    customers = load_customers()
    visits = load_visits()

    customer_id = input("고객 ID: ").strip()
    customer = require_customer(customers, customer_id)

    if not customer:
        return

    customer_visits = [
        visit for visit in visits if visit["customer_id"] == customer_id
    ]

    if not customer_visits:
        print("등록된 방문 기록이 없습니다.")
        return

    print(f"\n[{customer['name']}] 방문 기록\n")

    for visit in customer_visits:
        print_visit(visit)

    print(f"\n총 방문 횟수 : {len(customer_visits)}회\n")


def show_menu():
    print("\n=== 피부관리샵 고객 관리 프로그램 ===")
    print("1. 고객 등록")
    print("2. 고객 목록 조회")
    print("3. 고객 검색")
    print("4. 고객 정보 수정")
    print("5. 고객 삭제")
    print("6. 방문 기록 등록")
    print("7. 고객별 방문 기록 조회")
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
    initialize_csv()

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
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 메뉴입니다.")


if __name__ == "__main__":
    main()
