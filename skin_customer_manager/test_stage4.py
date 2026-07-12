"""4단계 보완 — services·backup 로직 테스트"""
import os
import sqlite3

import backup as backup_module
import database as db
from services import (
    check_customer_deletable,
    check_customer_updatable,
    prepare_customer_data,
    prepare_visit_data,
)

TEST_DB = "test_stage4.db"
TEST_BACKUP_DIR = "test_backup_stage4"
ORIGINAL_DB = db.DATABASE_FILE
ORIGINAL_BACKUP_DIR = backup_module.BACKUP_DIR


def setup():
    db.DATABASE_FILE = TEST_DB
    backup_module.DATABASE_FILE = TEST_DB
    backup_module.BACKUP_DIR = TEST_BACKUP_DIR

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    if os.path.exists(TEST_BACKUP_DIR):
        for filename in os.listdir(TEST_BACKUP_DIR):
            os.remove(os.path.join(TEST_BACKUP_DIR, filename))
        os.rmdir(TEST_BACKUP_DIR)

    db.initialize_database()


def teardown():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    if os.path.exists(TEST_BACKUP_DIR):
        for filename in os.listdir(TEST_BACKUP_DIR):
            os.remove(os.path.join(TEST_BACKUP_DIR, filename))
        os.rmdir(TEST_BACKUP_DIR)

    db.DATABASE_FILE = ORIGINAL_DB
    backup_module.DATABASE_FILE = ORIGINAL_DB
    backup_module.BACKUP_DIR = ORIGINAL_BACKUP_DIR


def test_customer_register_success():
    result = prepare_customer_data("김민지", "010-1234-5678")
    assert result.ok
    assert result.data["name"] == "김민지"
    print("[OK] 고객 등록 성공 검증")


def test_customer_required_fields():
    assert not prepare_customer_data("", "010-1234-5678").ok
    assert not prepare_customer_data("김민지", "").ok
    print("[OK] 이름/연락처 필수 검증")


def test_duplicate_phone():
    db.insert_customer("첫고객", "010-1111-2222", "", "", "", "2025-01-01")
    result = prepare_customer_data("둘째고객", "010-1111-2222")
    assert not result.ok
    assert "이미 등록된 연락처" in result.message
    print("[OK] 연락처 중복 등록 차단")


def test_duplicate_phone_exclude_self_on_update():
    customer_id = db.insert_customer("수정고객", "010-9999-8888", "", "", "", "2025-01-01")
    result = prepare_customer_data(
        "수정고객",
        "010-9999-8888",
        exclude_customer_id=customer_id,
    )
    assert result.ok
    print("[OK] 본인 연락처 수정 허용")


def test_invalid_visit_date_and_price():
    customer_id = db.insert_customer("방문고객", "010-2222-3333", "", "", "", "2025-01-01")

    bad_date = prepare_visit_data(customer_id, "20250312", "관리", "10000", "")
    assert not bad_date.ok

    bad_price = prepare_visit_data(customer_id, "2025-03-12", "관리", "-100", "")
    assert not bad_price.ok

    print("[OK] 잘못된 날짜/음수 가격 검증")


def test_customer_delete_blocked_with_visits():
    customer_id = db.insert_customer("삭제불가", "010-3333-4444", "", "", "", "2025-01-01")
    db.insert_visit(customer_id, "2025-03-01", "관리", 50000, "")
    result = check_customer_deletable(customer_id)
    assert not result.ok
    assert "방문 기록" in result.message
    print("[OK] 방문 있는 고객 삭제 차단")


def test_customer_update_without_selection():
    result = check_customer_updatable(None)
    assert not result.ok
    print("[OK] 미선택 수정 차단")


def test_backup_and_restore():
    customer_id = db.insert_customer("백업고객", "010-5555-6666", "", "", "", "2025-01-01")
    backup_path = backup_module.create_backup()
    assert os.path.exists(backup_path)

    db.delete_customer(customer_id)
    assert db.get_customer_by_id(customer_id) is None

    backup_name = os.path.basename(backup_path)
    backup_module.restore_backup(backup_name)
    restored = db.get_customer_by_id(customer_id)
    assert restored is not None
    assert restored["name"] == "백업고객"
    print("[OK] DB 백업/복원")


def test_customer_stats():
    customer_id = db.insert_customer("통계고객", "010-7777-8888", "", "", "", "2025-01-01")
    db.insert_visit(customer_id, "2025-03-01", "관리A", 50000, "")
    db.insert_visit(customer_id, "2025-03-15", "관리B", 70000, "")

    customers = db.load_customers_with_stats()
    target = next(c for c in customers if c["name"] == "통계고객")
    assert target["last_visit_date"] == "2025-03-15"
    assert target["visit_count"] == "2"
    assert target["total_price"] == "120000"
    print("[OK] 고객 통계(최근 방문일/횟수/금액)")


def main():
    setup()
    try:
        test_customer_register_success()
        test_customer_required_fields()
        test_duplicate_phone()
        test_duplicate_phone_exclude_self_on_update()
        test_invalid_visit_date_and_price()
        test_customer_delete_blocked_with_visits()
        test_customer_update_without_selection()
        test_backup_and_restore()
        test_customer_stats()
        print("\n=== 4단계 보완 테스트 통과 ===")
    finally:
        teardown()


if __name__ == "__main__":
    main()
