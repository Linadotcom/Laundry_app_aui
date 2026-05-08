# Laundry Management System

CSC 3326 Project - AUI 4th Semester

## Prerequisites
- Python 3.8+
- PostgreSQL

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd LaundryProject
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Copy `.env.example` to `.env` and fill in your PostgreSQL credentials.

### 4. Run database migrations
```bash
python run_migrations.py
```

### 5. Start the app
```bash
python app.py
```

---

## Database Migrations

### After every `git pull`
If the `migrations/` folder has new files, run:
```bash
python run_migrations.py
```

To verify everything is in order:
```bash
python verify_migrations.py
```

### What the triggers do

| Trigger | Fires when | Effect |
|---|---|---|
| `trg_machine_start` | Order inserted with machine_id | Sets machine → **Busy** |
| `trg_sync_machine_busy` | Order updated with machine_id / In Progress | Sets machine → **Busy** |
| `trg_sync_machine_available` | Order status → Completed / Picked Up, or machine_id cleared | Sets machine → **Available** |

This means direct SQL updates (e.g. in psql) automatically keep `Laundry_Machine.current_status` in sync — no manual steps needed.