# py-get-hdc

เครื่องมือสำหรับดึงข้อมูลจาก MOPH Open Data API และบันทึกลงฐานข้อมูล MySQL (Upsert)

## วิธีการใช้งาน

### 1. ติดตั้ง Dependencies
ใช้ `uv` เพื่อจัดการ dependencies:
```bash
uv sync
```

### 2. ตั้งค่า Environment Variables
สร้างไฟล์ `.env` และกำหนดค่าดังนี้:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=43files
```

### 3. รันสคริปต์
คุณสามารถรันได้หลายวิธี:

**รันผ่านสคริปต์หลักทันที:**
```bash
uv run py-get-hdc.py
```

**รันผ่าน Scheduler (เพื่อรันตามเวลาที่กำหนด):**
```bash
uv run scheduler
```
หรือ
```bash
uv run scheduler.py
```

## โครงสร้างโปรเจกต์
- `py-get-hdc.py`: สคริปต์หลักในการดึงข้อมูลและบันทึกฐานข้อมูล
- `scheduler.py`: ระบบตั้งเวลารันงานอัตโนมัติ
- `pyproject.toml`: การตั้งค่าโปรเจกต์และ dependencies
