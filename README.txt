NAFSIN AGRO VALLEY - V1.0 (Starter MVP)
========================================

Requirements:
- Windows 10
- Python 3.11 or newer (64-bit)
- Internet connection for the first dependency installation only

How to run:
1. Install Python from https://www.python.org/downloads/windows/
2. During installation, tick "Add Python to PATH".
3. Extract this ZIP to a normal folder, e.g. C:\NafsinAgro.
4. Double-click START_NAFSIN_AGRO.bat.
5. Wait for installation. Your browser should open the local app.
6. If it does not, open http://localhost:8501

Database:
- Created automatically as nafsin_agro.db in this folder.
- Use Data Backup menu to create a backup.
- Do not delete the .db file.

Included in V1:
- Poultry batch creation
- Poultry daily mortality/feed/weight/cost entry
- Fish pond creation
- Fish daily mortality/feed/weight/water-quality entry
- Income and expense transaction entry
- Basic double-entry journal for cash/bank income and expense
- Trial balance and basic P&L
- Manual database backup
- Bangla/English interface selector

Important limitations:
- This is an initial local single-PC MVP, not yet a production multi-user cloud system.
- Full accounting is NOT complete: no customer/vendor subledgers, receivables/payables,
  inventory valuation, stock movement costing, bank reconciliation, depreciation,
  VAT/tax, balance sheet closing or audit approval workflow.
- Do not use it as the only official accounting record until validated by an accountant.
- For 3-5 simultaneous users, deploy to a secured server and migrate SQLite to PostgreSQL.
- Keep backups on a separate drive.
