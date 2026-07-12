"""3단계 SQLite 기능 전체 테스트"""
import os
import sqlite3

import database as db

TEST_DB = "test_skin_shop.db"
ORIGINAL_DB = db.DATABASE_FILE


def setup():
    db.DATABASE_FILE = TEST_DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.initialize_database()


def teardown():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.DATABASE_FILE = ORIGINAL_DB


def test_db_and_tables():
    assert os.path.exists(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()
    assert "customers" in tables
    assert "visits" in tables
    print("[OK] SQLite DB 생성 + customers/visits 테이블")


def test_foreign_key():
    cid = db.insert_customer("테스트", "010-1111-2222", "", "", "", "2025-01-01")
    db.insert_visit(cid, "2025-03-01", "관리", 50000, "")
    try:
        db.delete_customer(cid)
        assert False, "FK 제약으로 삭제가 막혀야 함"
    except sqlite3.IntegrityError:
        pass
    print("[OK] Foreign Key 제약")


def test_customer_crud():
    cid = db.insert_customer("김민지", "010-1234-5678", "1990-01-01", "건성", "VIP", "2025-01-01")
    assert str(cid) == "1" or cid >= 1

    customer = db.get_customer_by_id(cid)
    assert customer["name"] == "김민지"

    db.update_customer(cid, "김민지2", "010-9999-8888", "1990-01-01", "지성", "수정됨")
    updated = db.get_customer_by_id(cid)
    assert updated["name"] == "김민지2"
    assert updated["phone"] == "010-9999-8888"

    customers = db.load_customers()
    assert len(customers) >= 2

    # FK 있는 고객은 삭제 불가 — 방문 없는 고객만 삭제 테스트
    cid2 = db.insert_customer("삭제대상", "010-0000-0000", "", "", "", "2025-01-01")
    db.delete_customer(cid2)
    assert db.get_customer_by_id(cid2) is None
    print("[OK] SQL CRUD (customers)")


def test_visit_crud():
    customers = db.load_customers()
    kim = next(c for c in customers if c["name"] == "김민지2")
    cid = kim["id"]
    db.insert_visit(cid, "2025-03-10", "딥클렌징", 80000, "첫 방문")
    visits = db.get_visits_by_customer_id(cid)
    assert len(visits) >= 1
    assert visits[-1]["service"] == "딥클렌징"
    assert db.customer_has_visits(cid)

    visit_id = visits[-1]["visit_id"]
    visit = db.get_visit_by_id(visit_id)
    assert visit is not None
    assert visit["service"] == "딥클렌징"

    db.update_visit(visit_id, cid, "2025-03-11", "수분관리", 60000, "수정됨")
    updated = db.get_visit_by_id(visit_id)
    assert updated["date"] == "2025-03-11"
    assert updated["service"] == "수분관리"
    assert updated["price"] == "60000"
    assert updated["memo"] == "수정됨"

    db.delete_visit(visit_id)
    assert db.get_visit_by_id(visit_id) is None
    assert not db.customer_has_visits(cid)
    print("[OK] SQL CRUD (visits Create/Read/Update/Delete)")


def test_search():
    results = db.search_customers("민지")
    assert any(c["name"] == "김민지2" for c in results)

    results = db.search_customers("9999")
    assert any("9999" in c["phone"] for c in results)

    results = db.search_customers("없는검색어xyz")
    assert results == []
    print("[OK] 검색 기능 (SQLite LIKE)")


def test_join():
    kim = next(c for c in db.load_customers() if c["name"] == "김민지2")
    db.insert_visit(kim["id"], "2025-03-12", "필링", 70000, "JOIN 테스트")
    customer, visits = db.get_visits_with_customer_by_id(kim["id"])
    assert customer is not None
    assert len(visits) >= 1
    assert "customer_name" in visits[0] or customer["name"]

    all_visits = db.get_all_visits_with_customer()
    assert len(all_visits) >= 1
    names = {v["customer_name"] for v in all_visits}
    assert "김민지2" in names
    print("[OK] JOIN 조회")


def test_persistence():
    db.DATABASE_FILE = TEST_DB
    customers_before = len(db.load_customers())
    db.initialize_database()
    customers_after = len(db.load_customers())
    assert customers_before == customers_after
    print("[OK] DB 재시작 후 데이터 유지")


def main():
    setup()
    try:
        test_db_and_tables()
        test_foreign_key()
        test_customer_crud()
        test_visit_crud()
        test_search()
        test_join()
        test_persistence()
        print("\n=== 3단계 전체 테스트 통과 ===")
    finally:
        teardown()


if __name__ == "__main__":
    main()
