import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from backup import create_backup, list_backups, restore_backup
from database import (
    delete_customer as db_delete_customer,
    delete_visit as db_delete_visit,
    get_all_visits_with_customer,
    get_customer_by_id,
    get_visit_by_id,
    initialize_database,
    insert_customer,
    insert_visit,
    load_customers,
    search_customers,
    update_customer as db_update_customer,
    update_visit as db_update_visit,
)
from services import (
    check_customer_deletable,
    check_customer_updatable,
    check_visit_deletable,
    check_visit_updatable,
    prepare_customer_data,
    prepare_visit_data,
)


class SkinShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("피부관리샵 고객 관리")
        self.geometry("960x640")
        self.minsize(800, 560)

        initialize_database()

        self._create_variables()
        self._create_widgets()
        self._bind_events()
        self.on_load_customers()
        self.on_load_visits()

    def _create_variables(self):
        self.customer_name_var = tk.StringVar()
        self.customer_phone_var = tk.StringVar()
        self.customer_birth_var = tk.StringVar()
        self.customer_skin_type_var = tk.StringVar()
        self.customer_memo_var = tk.StringVar()
        self.customer_search_var = tk.StringVar()

        self.visit_customer_var = tk.StringVar()
        self.visit_date_var = tk.StringVar()
        self.visit_service_var = tk.StringVar()
        self.visit_price_var = tk.StringVar()
        self.visit_memo_var = tk.StringVar()

        self.selected_customer_id = None
        self.selected_visit_id = None

    def _create_widgets(self):
        self._create_backup_bar()

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.customer_tab = ttk.Frame(notebook, padding=10)
        self.visit_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.customer_tab, text="고객 관리")
        notebook.add(self.visit_tab, text="방문 기록")

        self._build_customer_tab()
        self._build_visit_tab()

    def _create_backup_bar(self):
        bar = ttk.Frame(self, padding=(10, 10, 10, 0))
        bar.pack(fill=tk.X)

        ttk.Label(bar, text="데이터 관리").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(bar, text="DB 백업", command=self.on_backup_db).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(bar, text="백업 복원", command=self.on_restore_db).pack(side=tk.LEFT)

    def _build_customer_tab(self):
        form_frame = ttk.LabelFrame(self.customer_tab, text="고객 정보", padding=10)
        form_frame.pack(fill=tk.X)

        fields = [
            ("이름", self.customer_name_var),
            ("연락처", self.customer_phone_var),
            ("생년월일", self.customer_birth_var),
            ("피부 타입", self.customer_skin_type_var),
            ("메모", self.customer_memo_var),
        ]

        for row, (label, variable) in enumerate(fields):
            ttk.Label(form_frame, text=label, width=10).grid(
                row=row, column=0, sticky=tk.W, pady=4
            )
            ttk.Entry(form_frame, textvariable=variable, width=40).grid(
                row=row, column=1, sticky=tk.EW, pady=4
            )

        form_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(self.customer_tab)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="등록", command=self.on_add_customer).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="수정", command=self.on_update_customer).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="삭제", command=self.on_delete_customer).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="입력 초기화", command=self.clear_customer_form).pack(
            side=tk.LEFT, padx=(0, 6)
        )

        search_frame = ttk.Frame(self.customer_tab)
        search_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(search_frame, text="검색").pack(side=tk.LEFT)
        ttk.Entry(search_frame, textvariable=self.customer_search_var, width=30).pack(
            side=tk.LEFT, padx=(8, 6)
        )
        ttk.Button(search_frame, text="검색", command=self.on_search_customers).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(search_frame, text="전체 보기", command=self.on_load_customers).pack(
            side=tk.LEFT
        )

        table_frame = ttk.LabelFrame(self.customer_tab, text="고객 목록", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.customer_table_frame = table_frame

        columns = ("id", "name", "phone", "birth", "skin_type", "created_at")
        self.customer_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )

        headings = {
            "id": "ID",
            "name": "이름",
            "phone": "연락처",
            "birth": "생년월일",
            "skin_type": "피부 타입",
            "created_at": "등록일",
        }
        widths = {
            "id": 50,
            "name": 100,
            "phone": 120,
            "birth": 100,
            "skin_type": 80,
            "created_at": 140,
        }

        for column in columns:
            self.customer_tree.heading(column, text=headings[column])
            self.customer_tree.column(column, width=widths[column], anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.customer_tree.yview
        )
        self.customer_tree.configure(yscrollcommand=scrollbar.set)

        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_visit_tab(self):
        form_frame = ttk.LabelFrame(self.visit_tab, text="방문 기록", padding=10)
        form_frame.pack(fill=tk.X)

        ttk.Label(form_frame, text="고객", width=10).grid(
            row=0, column=0, sticky=tk.W, pady=4
        )
        self.visit_customer_combo = ttk.Combobox(
            form_frame,
            textvariable=self.visit_customer_var,
            state="readonly",
            width=38,
        )
        self.visit_customer_combo.grid(row=0, column=1, sticky=tk.EW, pady=4)

        visit_fields = [
            ("방문 날짜", self.visit_date_var),
            ("시술 내용", self.visit_service_var),
            ("가격", self.visit_price_var),
            ("메모", self.visit_memo_var),
        ]

        for row, (label, variable) in enumerate(visit_fields, start=1):
            ttk.Label(form_frame, text=label, width=10).grid(
                row=row, column=0, sticky=tk.W, pady=4
            )
            ttk.Entry(form_frame, textvariable=variable, width=40).grid(
                row=row, column=1, sticky=tk.EW, pady=4
            )

        form_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(self.visit_tab)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="기록 추가", command=self.on_add_visit).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="수정", command=self.on_update_visit).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="삭제", command=self.on_delete_visit).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="입력 초기화", command=self.clear_visit_form).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="새로고침", command=self.on_load_visits).pack(
            side=tk.LEFT
        )

        table_frame = ttk.LabelFrame(self.visit_tab, text="방문 내역", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.visit_table_frame = table_frame

        columns = (
            "visit_id",
            "customer_name",
            "customer_id",
            "date",
            "service",
            "price",
            "memo",
        )
        self.visit_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )

        headings = {
            "visit_id": "방문 ID",
            "customer_name": "고객명",
            "customer_id": "고객 ID",
            "date": "방문 날짜",
            "service": "시술 내용",
            "price": "가격",
            "memo": "메모",
        }
        widths = {
            "visit_id": 70,
            "customer_name": 100,
            "customer_id": 70,
            "date": 100,
            "service": 120,
            "price": 80,
            "memo": 160,
        }

        for column in columns:
            self.visit_tree.heading(column, text=headings[column])
            self.visit_tree.column(column, width=widths[column], anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.visit_tree.yview
        )
        self.visit_tree.configure(yscrollcommand=scrollbar.set)

        self.visit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _bind_events(self):
        self.customer_tree.bind("<<TreeviewSelect>>", self.on_customer_selected)
        self.visit_tree.bind("<<TreeviewSelect>>", self.on_visit_selected)

    def clear_customer_form(self):
        self.customer_name_var.set("")
        self.customer_phone_var.set("")
        self.customer_birth_var.set("")
        self.customer_skin_type_var.set("")
        self.customer_memo_var.set("")
        self.selected_customer_id = None
        self.customer_tree.selection_remove(self.customer_tree.selection())

    def _get_customer_form_data(self, exclude_customer_id=None):
        result = prepare_customer_data(
            name=self.customer_name_var.get(),
            phone=self.customer_phone_var.get(),
            birth=self.customer_birth_var.get(),
            skin_type=self.customer_skin_type_var.get(),
            memo=self.customer_memo_var.get(),
            exclude_customer_id=exclude_customer_id,
        )
        if not result.ok:
            messagebox.showwarning("입력 오류", result.message)
            return None
        return result.data

    def on_backup_db(self):
        try:
            backup_path = create_backup()
            messagebox.showinfo("백업 완료", f"백업 파일이 생성되었습니다.\n{backup_path}")
        except FileNotFoundError as error:
            messagebox.showwarning("백업 실패", str(error))

    def on_restore_db(self):
        backups = list_backups()
        if not backups:
            messagebox.showinfo("복원", "백업 파일이 없습니다.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("백업 복원")
        dialog.geometry("420x300")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="복원할 백업 파일을 선택하세요.").pack(
            anchor=tk.W, padx=12, pady=(12, 6)
        )

        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        for backup_name in backups:
            listbox.insert(tk.END, backup_name)
        if backups:
            listbox.selection_set(0)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        def restore_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("선택 오류", "복원할 백업 파일을 선택해주세요.")
                return

            backup_name = listbox.get(selection[0])
            confirmed = messagebox.askyesno(
                "복원 확인",
                f"현재 DB를 '{backup_name}' 파일로 복원합니다.\n"
                "현재 데이터는 덮어씌워집니다. 계속하시겠습니까?",
                parent=dialog,
            )
            if not confirmed:
                return

            try:
                restore_backup(backup_name)
            except FileNotFoundError as error:
                messagebox.showwarning("복원 실패", str(error), parent=dialog)
                return

            messagebox.showinfo("복원 완료", "DB가 복원되었습니다.", parent=dialog)
            dialog.destroy()
            self.clear_customer_form()
            self.clear_visit_form()
            self.on_load_customers()
            self.on_load_visits()

        ttk.Button(button_frame, text="복원", command=restore_selected).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(button_frame, text="닫기", command=dialog.destroy).pack(side=tk.LEFT)

    def _populate_customer_tree(self, customers):
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        for customer in customers:
            self.customer_tree.insert(
                "",
                tk.END,
                iid=customer["id"],
                values=(
                    customer["id"],
                    customer["name"],
                    customer["phone"],
                    customer["birth"],
                    customer["skin_type"],
                    customer.get("created_at", ""),
                ),
            )

        self.customer_table_frame.configure(text=f"고객 목록 — 총 {len(customers)}명")

    def _refresh_visit_customer_combo(self):
        customers = load_customers()
        options = [f"{customer['id']} - {customer['name']}" for customer in customers]
        self.visit_customer_combo["values"] = options

    def on_customer_selected(self, _event=None):
        selection = self.customer_tree.selection()
        if not selection:
            return

        customer_id = selection[0]
        customer = get_customer_by_id(customer_id)
        if not customer:
            return

        self.selected_customer_id = customer["id"]
        self.customer_name_var.set(customer["name"])
        self.customer_phone_var.set(customer["phone"])
        self.customer_birth_var.set(customer["birth"])
        self.customer_skin_type_var.set(customer["skin_type"])
        self.customer_memo_var.set(customer["memo"])

    def on_load_customers(self):
        customers = load_customers()
        self._populate_customer_tree(customers)
        self._refresh_visit_customer_combo()

    def on_search_customers(self):
        keyword = self.customer_search_var.get().strip()
        if not keyword:
            messagebox.showwarning("입력 오류", "검색어를 입력해주세요.")
            return

        results = search_customers(keyword)
        if not results:
            messagebox.showinfo("검색 결과", "검색 결과가 없습니다.")
            self._populate_customer_tree([])
            return

        self._populate_customer_tree(results)

    def on_add_customer(self):
        data = self._get_customer_form_data()
        if not data:
            return

        insert_customer(
            name=data["name"],
            phone=data["phone"],
            birth=data["birth"],
            skin_type=data["skin_type"],
            memo=data["memo"],
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        messagebox.showinfo("완료", "고객이 등록되었습니다.")
        self.clear_customer_form()
        self.on_load_customers()

    def on_update_customer(self):
        check = check_customer_updatable(self.selected_customer_id)
        if not check.ok:
            messagebox.showwarning("선택 오류", check.message)
            return

        data = self._get_customer_form_data(exclude_customer_id=self.selected_customer_id)
        if not data:
            return

        db_update_customer(
            customer_id=self.selected_customer_id,
            name=data["name"],
            phone=data["phone"],
            birth=data["birth"],
            skin_type=data["skin_type"],
            memo=data["memo"],
        )
        messagebox.showinfo("완료", "고객 정보가 수정되었습니다.")
        self.on_load_customers()

        if self.customer_tree.exists(self.selected_customer_id):
            self.customer_tree.selection_set(self.selected_customer_id)
            self.customer_tree.focus(self.selected_customer_id)
            self.on_customer_selected()

    def on_delete_customer(self):
        check = check_customer_deletable(self.selected_customer_id)
        if not check.ok:
            messagebox.showwarning("삭제 불가" if "방문 기록" in check.message else "선택 오류", check.message)
            return

        customer = check.data

        confirmed = messagebox.askyesno(
            "삭제 확인",
            f"[{customer['name']}] 고객을 정말 삭제하시겠습니까?",
        )
        if not confirmed:
            return

        db_delete_customer(self.selected_customer_id)
        messagebox.showinfo("완료", "고객 정보가 삭제되었습니다.")
        self.clear_customer_form()
        self.on_load_customers()

    def clear_visit_form(self):
        self.visit_customer_var.set("")
        self.visit_date_var.set("")
        self.visit_service_var.set("")
        self.visit_price_var.set("")
        self.visit_memo_var.set("")
        self.selected_visit_id = None
        self.visit_tree.selection_remove(self.visit_tree.selection())

    def _set_visit_customer_combo(self, customer_id):
        customer = get_customer_by_id(customer_id)
        if customer:
            self.visit_customer_var.set(f"{customer['id']} - {customer['name']}")

    def _get_selected_visit_customer_id(self):
        value = self.visit_customer_var.get().strip()
        if not value:
            messagebox.showwarning("입력 오류", "고객을 선택해주세요.")
            return None

        customer_id = value.split(" - ", 1)[0].strip()
        if not customer_id.isdigit():
            messagebox.showwarning("입력 오류", "고객을 다시 선택해주세요.")
            return None

        customer = get_customer_by_id(customer_id)
        if not customer:
            messagebox.showwarning("입력 오류", "해당 고객을 찾을 수 없습니다.")
            return None

        return customer_id

    def _get_visit_form_data(self):
        customer_id = self._get_selected_visit_customer_id()
        if customer_id is None:
            return None

        result = prepare_visit_data(
            customer_id=customer_id,
            date=self.visit_date_var.get(),
            service=self.visit_service_var.get(),
            price=self.visit_price_var.get(),
            memo=self.visit_memo_var.get(),
        )
        if not result.ok:
            messagebox.showwarning("입력 오류", result.message)
            return None
        return result.data

    def _populate_visit_tree(self, visits):
        for item in self.visit_tree.get_children():
            self.visit_tree.delete(item)

        for visit in visits:
            self.visit_tree.insert(
                "",
                tk.END,
                iid=visit["visit_id"],
                values=(
                    visit["visit_id"],
                    visit["customer_name"],
                    visit["customer_id"],
                    visit["date"],
                    visit["service"],
                    visit["price"],
                    visit["memo"],
                ),
            )

        self.visit_table_frame.configure(text=f"방문 내역 — 총 {len(visits)}건")

    def on_visit_selected(self, _event=None):
        selection = self.visit_tree.selection()
        if not selection:
            return

        visit_id = selection[0]
        visit = get_visit_by_id(visit_id)
        if not visit:
            return

        self.selected_visit_id = visit["visit_id"]
        self._set_visit_customer_combo(visit["customer_id"])
        self.visit_date_var.set(visit["date"])
        self.visit_service_var.set(visit["service"])
        self.visit_price_var.set(visit["price"])
        self.visit_memo_var.set(visit["memo"])

    def on_load_visits(self):
        visits = get_all_visits_with_customer()
        self._populate_visit_tree(visits)

    def on_add_visit(self):
        data = self._get_visit_form_data()
        if not data:
            return

        insert_visit(
            customer_id=data["customer_id"],
            date=data["date"],
            service=data["service"],
            price=data["price"],
            memo=data["memo"],
        )
        messagebox.showinfo("완료", "방문 기록이 등록되었습니다.")
        self.clear_visit_form()
        self.on_load_visits()

    def on_update_visit(self):
        check = check_visit_updatable(self.selected_visit_id)
        if not check.ok:
            messagebox.showwarning("선택 오류", check.message)
            return

        data = self._get_visit_form_data()
        if not data:
            return

        db_update_visit(
            visit_id=self.selected_visit_id,
            customer_id=data["customer_id"],
            date=data["date"],
            service=data["service"],
            price=data["price"],
            memo=data["memo"],
        )
        messagebox.showinfo("완료", "방문 기록이 수정되었습니다.")
        self.on_load_visits()

        if self.visit_tree.exists(self.selected_visit_id):
            self.visit_tree.selection_set(self.selected_visit_id)
            self.visit_tree.focus(self.selected_visit_id)
            self.on_visit_selected()

    def on_delete_visit(self):
        check = check_visit_deletable(self.selected_visit_id)
        if not check.ok:
            messagebox.showwarning("선택 오류", check.message)
            return

        visit = check.data

        confirmed = messagebox.askyesno(
            "삭제 확인",
            f"방문 ID {visit['visit_id']} 기록을 정말 삭제하시겠습니까?",
        )
        if not confirmed:
            return

        db_delete_visit(self.selected_visit_id)
        messagebox.showinfo("완료", "방문 기록이 삭제되었습니다.")
        self.clear_visit_form()
        self.on_load_visits()


def main():
    app = SkinShopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
