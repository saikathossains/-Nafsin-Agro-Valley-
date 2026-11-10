import streamlit as st
import sqlite3, os
from datetime import date, datetime
from pathlib import Path
import pandas as pd

APP_DIR = Path(_file_).resolve().parent
DB = APP_DIR / "nafsin_agro.db"
st.set_page_config(page_title="Nafsin Agro Valley", page_icon="🌱", layout="wide")

def conn():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS poultry_batches(
          id INTEGER PRIMARY KEY AUTOINCREMENT, batch_name TEXT, bird_type TEXT,
          start_date TEXT, opening_birds INTEGER, purchase_cost REAL DEFAULT 0, notes TEXT);
        CREATE TABLE IF NOT EXISTS poultry_daily(
          id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id INTEGER, entry_date TEXT,
          mortality INTEGER DEFAULT 0, feed_kg REAL DEFAULT 0, avg_weight_g REAL DEFAULT 0,
          medicine_cost REAL DEFAULT 0, other_cost REAL DEFAULT 0, notes TEXT);
        CREATE TABLE IF NOT EXISTS ponds(
          id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, area_decimal REAL DEFAULT 0,
          depth_ft REAL DEFAULT 0, species TEXT, stocking_date TEXT, stocked_fish INTEGER DEFAULT 0,
          stocking_cost REAL DEFAULT 0, notes TEXT);
        CREATE TABLE IF NOT EXISTS fish_daily(
          id INTEGER PRIMARY KEY AUTOINCREMENT, pond_id INTEGER, entry_date TEXT,
          mortality INTEGER DEFAULT 0, feed_kg REAL DEFAULT 0, avg_weight_g REAL DEFAULT 0,
          medicine_cost REAL DEFAULT 0, other_cost REAL DEFAULT 0, ph REAL, do_mg REAL, temp_c REAL, notes TEXT);
        CREATE TABLE IF NOT EXISTS transactions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, txn_date TEXT, txn_type TEXT,
          category TEXT, description TEXT, amount REAL, payment_account TEXT DEFAULT 'Cash');
        CREATE TABLE IF NOT EXISTS accounts(
          code TEXT PRIMARY KEY, name TEXT, account_type TEXT);
        CREATE TABLE IF NOT EXISTS journal(
          id INTEGER PRIMARY KEY AUTOINCREMENT, txn_id INTEGER, txn_date TEXT,
          account_code TEXT, debit REAL DEFAULT 0, credit REAL DEFAULT 0, memo TEXT);
        """)
        defaults=[
        ('1000','Cash','Asset'),('1010','Bank','Asset'),('1200','Inventory','Asset'),
        ('2000','Accounts Payable','Liability'),('3000','Owner Capital','Equity'),
        ('4000','Farm Sales','Income'),('5000','Feed Expense','Expense'),
        ('5100','Medicine Expense','Expense'),('5200','Chick/Fish Stock Expense','Expense'),
        ('5300','Other Farm Expense','Expense')]
        for x in defaults:
            c.execute("INSERT OR IGNORE INTO accounts VALUES(?,?,?)",x)
init()

def q(sql,args=()):
    with conn() as c: return c.execute(sql,args).fetchall()
def run(sql,args=()):
    with conn() as c:
        cur=c.execute(sql,args); c.commit(); return cur.lastrowid
def money(x): return f"৳{float(x or 0):,.2f}"
def tr(en,bn):
    return f"{bn} / {en}" if st.session_state.get("lang","বাংলা")=="বাংলা" else en

st.sidebar.title("🌱 Nafsin Agro Valley")
st.sidebar.caption("Farm Management System • V1.0")
st.sidebar.selectbox("Language / ভাষা",["বাংলা","English"],key="lang")
menu=st.sidebar.radio("Menu / মেনু",[
"Dashboard","Poultry Batches","Poultry Daily Entry","Fish Ponds","Fish Daily Entry",
"Accounts & Transactions","Accounting Reports","Data Backup"])
st.sidebar.caption("Currency: BDT (৳) • Local database")

st.title("🌱 NAFSIN AGRO VALLEY")
st.caption("Integrated Poultry & Fish Farm Management | Version 1.0")

if menu=="Dashboard":
    st.subheader(tr("Farm Dashboard","খামারের ড্যাশবোর্ড"))
    batches=q("SELECT * FROM poultry_batches")
    ponds=q("SELECT * FROM ponds")
    birds=sum(x["opening_birds"] for x in batches)
    pmort=sum(x["mortality"] for x in q("SELECT mortality FROM poultry_daily"))
    fstock=sum(x["stocked_fish"] for x in ponds)
    fmor…
