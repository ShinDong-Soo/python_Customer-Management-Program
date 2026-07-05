import csv
import os


FILE_NAME = "customers.csv"
FIELDNAMES = ["id", "name", "phone", "birth", "skin_type", "memo"]


def initialize_csv():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def load_customers():
    customers = []

    with open(FILE_NAME, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            customers.append(row)

    return customers


def save_customers(customers):
    with open(FILE_NAME, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(customers)


def get_next_id(customers):
    if not customers:
        return 1

    max_id = max(int(customer["id"]) for customer in customers)
    return max_id + 1


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
        "memo": memo
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
    customer_id = input("수정할 고객 ID: ")

    for customer in customers:
        if customer["id"] == customer_id:
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
            return

    print("해당 ID의 고객을 찾을 수 없습니다.")


def delete_customer():
    customers = load_customers()
    customer_id = input("삭제할 고객 ID: ")

    new_customers = [
        customer
        for customer in customers
        if customer["id"] != customer_id
    ]

    if len(customers) == len(new_customers):
        print("해당 ID의 고객을 찾을 수 없습니다.")
        return

    confirm = input("정말 삭제하시겠습니까? (Y/N): ")

    if confirm.upper() != "Y":
        print("삭제가 취소되었습니다.")
        return

    save_customers(new_customers)
    print("고객 정보가 삭제되었습니다.")


def show_menu():
    print("\n=== 피부관리샵 고객 관리 프로그램 ===")
    print("1. 고객 등록")
    print("2. 고객 목록 조회")
    print("3. 고객 검색")
    print("4. 고객 정보 수정")
    print("5. 고객 삭제")
    print("0. 종료")


def print_customer(customer):
    print("-" * 40)
    print(f"ID: {customer['id']}")
    print(f"이름: {customer['name']}")
    print(f"연락처: {customer['phone']}")
    print(f"생년월일: {customer['birth']}")
    print(f"피부 타입: {customer['skin_type']}")
    print(f"메모: {customer['memo']}")


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
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 메뉴입니다.")


if __name__ == "__main__":
    main()
