import streamlit as st
import sqlite3, os
from datetime import date, datetime
from pathlib import Path
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
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
    fmort=sum(x["mortality"] for x in q("SELECT mortality FROM fish_daily"))
    income=sum(x["amount"] for x in q("SELECT amount FROM transactions WHERE txn_type='Income'"))
    expense=sum(x["amount"] for x in q("SELECT amount FROM transactions WHERE txn_type='Expense'"))
    a,b,c,d=st.columns(4)
    a.metric("Poultry opening birds",f"{birds:,}",f"Mortality {pmort:,}")
    b.metric("Fish stocked",f"{fstock:,}",f"Mortality {fmort:,}")
    c.metric("Income",money(income))
    d.metric("Expenses",money(expense))
    st.metric("Net operating result / নিট ফলাফল",money(income-expense))
    st.info("শুরু করতে Poultry Batches এবং Fish Ponds-এ আপনার খামারের তথ্য যোগ করুন। Dashboard-এর সংখ্যা আপনার এন্ট্রি করা ডেটা থেকে তৈরি হবে।")
    st.subheader("Recent transactions / সাম্প্রতিক লেনদেন")
    rows=q("SELECT * FROM transactions ORDER BY txn_date DESC,id DESC LIMIT 10")
    if rows: st.dataframe(pd.DataFrame([dict(x) for x in rows]),use_container_width=True)
    else: st.write("এখনো কোনো লেনদেন নেই। / No transactions yet.")

elif menu=="Poultry Batches":
    st.subheader("Poultry Batch Management / মুরগির ব্যাচ")
    with st.form("pb"):
        x1,x2=st.columns(2)
        name=x1.text_input("Batch name / ব্যাচের নাম")
        typ=x2.selectbox("Bird type / মুরগির ধরন",["Color Bird","Fumi","Broiler","Layer","Other"])
        x3,x4=st.columns(2)
        sd=x3.date_input("Start date / শুরুর তারিখ",date.today())
        qty=x4.number_input("Opening chicks / প্রাথমিক বাচ্চা",min_value=1,step=1)
        cost=st.number_input("Chick purchase cost (BDT) / বাচ্চার ক্রয়মূল্য",min_value=0.0)
        notes=st.text_area("Notes / মন্তব্য")
        if st.form_submit_button("Save batch / ব্যাচ সংরক্ষণ"):
            if name.strip():
                run("INSERT INTO poultry_batches(batch_name,bird_type,start_date,opening_birds,purchase_cost,notes) VALUES(?,?,?,?,?,?)",
                    (name,typ,str(sd),qty,cost,notes)); st.success("Batch saved.")
            else: st.error("Batch name is required.")
    rows=q("SELECT * FROM poultry_batches ORDER BY id DESC")
    if rows: st.dataframe(pd.DataFrame([dict(x) for x in rows]),use_container_width=True)

elif menu=="Poultry Daily Entry":
    st.subheader("Poultry Daily Record / দৈনিক মুরগির হিসাব")
    batches=q("SELECT * FROM poultry_batches ORDER BY id")
    if not batches: st.warning("প্রথমে Poultry Batches-এ একটি Batch তৈরি করুন।")
    else:
        opts={f'{x["batch_name"]} (ID {x["id"]})':x["id"] for x in batches}
        with st.form("pd"):
            bid=opts[st.selectbox("Batch",list(opts))]
            dt=st.date_input("Date",date.today())
            c1,c2,c3=st.columns(3)
            mort=c1.number_input("Mortality / মৃত্যু",min_value=0,step=1)
            feed=c2.number_input("Feed consumed (kg) / খাদ্য (কেজি)",min_value=0.0)
            wt=c3.number_input("Average weight (g) / গড় ওজন (গ্রাম)",min_value=0.0)
            c4,c5=st.columns(2)
            med=c4.number_input("Medicine cost (BDT)",min_value=0.0)
            other=c5.number_input("Other cost (BDT)",min_value=0.0)
            notes=st.text_area("Notes")
            if st.form_submit_button("Save daily record"):
                run("INSERT INTO poultry_daily(batch_id,entry_date,mortality,feed_kg,avg_weight_g,medicine_cost,other_cost,notes) VALUES(?,?,?,?,?,?,?,?)",
                    (bid,str(dt),mort,feed,wt,med,other,notes)); st.success("Daily record saved.")
        rows=q("SELECT d.*,b.batch_name FROM poultry_daily d LEFT JOIN poultry_batches b ON b.id=d.batch_id ORDER BY d.entry_date DESC")
        if rows: st.dataframe(pd.DataFrame([dict(x) for x in rows]),use_container_width=True)

elif menu=="Fish Ponds":
    st.subheader("Fish Pond Management / পুকুর ব্যবস্থাপনা")
    with st.form("pond"):
        a,b=st.columns(2)
        name=a.text_input("Pond name / পুকুরের নাম")
        species=b.selectbox("Species / মাছের প্রজাতি",["Pangasius","Tilapia","Carp","Mixed","Other"])
        c,d=st.columns(2)
        area=c.number_input("Area (decimal) / আয়তন (শতাংশ)",min_value=0.0)
        depth=d.number_input("Water depth (ft) / পানির গভীরতা (ফুট)",min_value=0.0)
        e,f=st.columns(2)
        sd=e.date_input("Stocking date / মাছ ছাড়ার তারিখ",date.today())
        qty=f.number_input("Stocked fish / মাছের সংখ্যা",min_value=0,step=1)
        cost=st.number_input("Stocking cost (BDT) / পোনা ক্রয়মূল্য",min_value=0.0)
        notes=st.text_area("Notes")
        if st.form_submit_button("Save pond"):
            if name.strip():
                run("INSERT INTO ponds(pond_name,area_decimal,depth_ft,species,stocking_date,stocked_fish,stocking_cost,notes) VALUES(?,?,?,?,?,?,?,?)",
                    (name,area,depth,species,str(sd),qty,cost,notes)); st.success("Pond saved.")
            else: st.error("Pond name is required.")
    rows=q("SELECT * FROM ponds ORDER BY id DESC")
    if rows: st.dataframe(pd.DataFrame([dict(x) for x in rows]),use_container_width=True)

elif menu=="Fish Daily Entry":
    st.subheader("Fish Daily Record / মাছের দৈনিক হিসাব")
    ponds=q("SELECT * FROM ponds ORDER BY id")
    if not ponds: st.warning("প্রথমে Fish Ponds-এ পুকুর যোগ করুন।")
    else:
        opts={f'{x["pond_name"]} (ID {x["id"]})':x["id"] for x in ponds}
        with st.form("fd"):
            pid=opts[st.selectbox("Pond",list(opts))]
            dt=st.date_input("Date",date.today())
            c1,c2,c3=st.columns(3)
            mort=c1.number_input("Mortality / মৃত্যু",min_value=0,step=1)
            feed=c2.number_input("Feed consumed (kg)",min_value=0.0)
            wt=c3.number_input("Average weight (g)",min_value=0.0)
            c4,c5,c6=st.columns(3)
            med=c4.number_input("Medicine cost (BDT)",min_value=0.0)
            other=c5.number_input("Other cost (BDT)",min_value=0.0)
            ph=c6.number_input("Water pH",min_value=0.0,max_value=14.0,value=7.0)
            c7,c8=st.columns(2)
            do=c7.number_input("DO (mg/L)",min_value=0.0)
            temp=c8.number_input("Temperature (°C)",min_value=0.0)
            notes=st.text_area("Notes")
            if st.form_submit_button("Save fish record"):
                run("INSERT INTO fish_daily(pond_id,entry_date,mortality,feed_kg,avg_weight_g,medicine_cost,other_cost,ph,do_mg,temp_c,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (pid,str(dt),mort,feed,wt,med,other,ph,do,temp,notes)); st.success("Fish record saved.")
        rows=q("SELECT d.*,p.pond_name FROM fish_daily d LEFT JOIN ponds p ON p.id=d.pond_id ORDER BY d.entry_date DESC")
        if rows: st.dataframe(pd.DataFrame([dict(x) for x in rows]),use_container_width=True)

elif menu=="Accounts & Transactions":
    st.subheader("Accounts & Transactions / হিসাব ও লেনদেন")
    st.caption("প্রতিটি Income/Expense-এর জন্য স্বয়ংক্রিয় Double-entry journal তৈরি হয়।")
    with st.form("txn"):
        dt=st.date_input("Transaction date / তারিখ",date.today())
        typ=st.selectbox("Type / ধরন",["Income","Expense"])
        cat=st.selectbox("Category / খাত",["Farm Sales","Feed Expense","Medicine Expense","Chick/Fish Stock Expense","Other Farm Expense","Other Income","Other Expense"])
        desc=st.text_input("Description / বিবরণ")
        amount=st.number_input("Amount (BDT) / পরিমাণ",min_value=0.01)
        pay=st.selectbox("Payment account",["Cash","Bank"])
        if st.form_submit_button("Save transaction"):
            tid=run("INSERT INTO transactions(txn_date,txn_type,category,description,amount,payment_account) VALUES(?,?,?,?,?,?)",
                    (str(dt),typ,cat,desc,amount,pay))
            cashcode="1000" if pay=="Cash" else "1010"
            if typ=="Income":
                run("INSERT INTO journal(txn_id,txn_date,account_code,debit,credit,memo) VALUES(?,?,?,?,?,?)",(tid,str(dt),cashcode,amount,0,desc))
                run("INSERT INTO journal(txn_id,txn_date,account_code,debit,credit,memo) VALUES(?,?,?,?,?,?)",(tid,str(dt),"4000",0,amount,desc))
            else:
                expensecode={"Feed Expense":"5000","Medicine Expense":"5100","Chick/Fish Stock Expense":"5200","Other Farm Expense":"5300","Other Expense":"5300"}.get(cat,"5300")
                run("INSERT INTO journal(txn_id,txn_date,account_code,debit,credit,memo) VALUES(?,?,?,?,?,?)",(tid,str(dt),expensecode,amount,0,desc))
                run("INSERT INTO journal(txn_id,txn_date,account_code,debit,credit,memo) VALUES(?,?,?,?,?,?)",(tid,str(dt),cashcode,0,amount,desc))
            st.success("Transaction and journal entries saved.")
    rows=q("SELECT * FROM transactions ORDER BY txn_date DESC,id DESC")
    if rows: st.dataframe(pd.DataFrame([dict(x) for x in rows]),use_container_width=True)

elif menu=="Accounting Reports":
    st.subheader("Accounting Reports / হিসাব প্রতিবেদন")
    j=q("""SELECT a.code,a.name,a.account_type,
      COALESCE(SUM(j.debit),0) debit, COALESCE(SUM(j.credit),0) credit
      FROM accounts a LEFT JOIN journal j ON j.account_code=a.code
      GROUP BY a.code,a.name,a.account_type ORDER BY a.code""")
    if j:
        df=pd.DataFrame([dict(x) for x in j])
        df["Balance (Dr positive)"]=df["debit"]-df["credit"]
        st.markdown("**Trial Balance / ট্রায়াল ব্যালেন্স**")
        st.dataframe(df,use_container_width=True)
        totaldr=df.debit.sum(); totalcr=df.credit.sum()
        c1,c2=st.columns(2); c1.metric("Total Debit",money(totaldr)); c2.metric("Total Credit",money(totalcr))
        st.metric("Trial Balance Difference",money(totaldr-totalcr))
        income=sum(r["credit"]-r["debit"] for r in j if r["account_type"]=="Income")
        expenses=sum(r["debit"]-r["credit"] for r in j if r["account_type"]=="Expense")
        st.subheader("Profit & Loss / লাভ-লোকসান")
        c1,c2,c3=st.columns(3)
        c1.metric("Income",money(income)); c2.metric("Expenses",money(expenses)); c3.metric("Net Profit",money(income-expenses))
        st.warning("এটি V1-এর basic cash/bank double-entry report। পূর্ণাঙ্গ Balance Sheet, receivables/payables, inventory valuation, depreciation, tax/VAT এবং year-end closing এখনো বাস্তবায়িত হয়নি।")
    else: st.info("কোনো হিসাবের তথ্য নেই।")

elif menu=="Data Backup":
    st.subheader("Database Backup / ডেটা ব্যাকআপ")
    st.write(f"Database location: `{DB}`")
    if st.button("Create backup now / এখনই ব্যাকআপ তৈরি করুন"):
        import shutil
        target=APP_DIR/f"backup_nafsin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB,target)
        st.success(f"Backup created: {target.name}")
    st.info("নিয়মিত Backup ফাইল অন্য USB drive বা নিরাপদ জায়গায় কপি রাখুন।")
