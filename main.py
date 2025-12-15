# -*- coding: utf-8 -*-
"""
تطبيق متابعة آراء العملاء للهاتف المحمول
يعمل بدون إنترنت - باللغة العربية
"""

import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.modalview import ModalView
from kivy.core.window import Window

Window.clearcolor = (0.95, 0.95, 0.95, 1)

DB_NAME = "customers.db"


# ======================
# قاعدة البيانات
# ======================
class Database:
    def __init__(self):
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product TEXT,
            status TEXT,
            notes TEXT
        )
        """)

        conn.commit()
        conn.close()

    def add_customer(self, name, phone):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO customers (name, phone) VALUES (?,?)", (name, phone))
        conn.commit()
        cid = c.lastrowid
        conn.close()
        return cid

    def add_feedback(self, cid, product, status, notes):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO feedback (customer_id, product, status, notes) VALUES (?,?,?,?)",
            (cid, product, status, notes),
        )
        conn.commit()
        conn.close()

    def get_all(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
        SELECT customers.name, customers.phone, feedback.product, feedback.status
        FROM customers
        LEFT JOIN feedback ON customers.id = feedback.customer_id
        ORDER BY customers.id DESC
        """)
        rows = c.fetchall()
        conn.close()
        return rows


# ======================
# الواجهة
# ======================
class AddScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)
        self.app = app

        self.name_input = TextInput(hint_text="اسم العميل", multiline=False)
        self.phone_input = TextInput(hint_text="رقم الهاتف", multiline=False)
        self.product_input = TextInput(hint_text="اسم المنتج", multiline=False)
        self.notes_input = TextInput(hint_text="ملاحظات", size_hint=(1, 0.3))

        self.add_widget(self.name_input)
        self.add_widget(self.phone_input)
        self.add_widget(self.product_input)
        self.add_widget(self.notes_input)

        box = BoxLayout(size_hint=(1, 0.2), spacing=10)
        self.pos_btn = ToggleButton(text="إيجابي", group="rate", state="down")
        self.neg_btn = ToggleButton(text="سلبي", group="rate")
        self.no_btn = ToggleButton(text="لم يرد", group="rate")
        box.add_widget(self.pos_btn)
        box.add_widget(self.neg_btn)
        box.add_widget(self.no_btn)

        self.add_widget(box)

        btn = Button(text="حفظ")
        btn.bind(on_press=self.save)
        self.add_widget(btn)

    def save(self, *_):
        name = self.name_input.text.strip()
        if not name:
            return

        phone = self.phone_input.text
        product = self.product_input.text
        notes = self.notes_input.text

        status = "إيجابي" if self.pos_btn.state == "down" else \
                 "سلبي" if self.neg_btn.state == "down" else "لم يرد"

        cid = self.app.db.add_customer(name, phone)
        self.app.db.add_feedback(cid, product, status, notes)

        self.name_input.text = ""
        self.phone_input.text = ""
        self.product_input.text = ""
        self.notes_input.text = ""


class ListScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation="vertical", padding=10, **kwargs)
        self.app = app
        self.scroll = ScrollView()
        self.list = GridLayout(cols=1, size_hint_y=None)
        self.list.bind(minimum_height=self.list.setter("height"))
        self.scroll.add_widget(self.list)
        self.add_widget(self.scroll)
        self.refresh()

    def refresh(self):
        self.list.clear_widgets()
        for name, phone, product, status in self.app.db.get_all():
            self.list.add_widget(
                Label(
                    text=f"{name} | {phone} | {product} | {status}",
                    size_hint_y=None,
                    height=40,
                )
            )


class CustomerApp(App):
    def build(self):
        self.title = "متابعة آراء العملاء"
        self.db = Database()

        tabs = TabbedPanel(do_default_tab=False)

        t1 = TabbedPanelItem(text="إضافة")
        t1.add_widget(AddScreen(self))
        tabs.add_widget(t1)

        t2 = TabbedPanelItem(text="العملاء")
        self.list_screen = ListScreen(self)
        t2.add_widget(self.list_screen)
        tabs.add_widget(t2)

        return tabs


if __name__ == "__main__":
    CustomerApp().run()
