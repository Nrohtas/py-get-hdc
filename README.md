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

### 3. รันสคริปต์ Sync ข้อมูล

คุณสามารถเลือกรัน sync แยกปี หรือรันพร้อมกันได้:

**Sync แยกปี 2570 (ปีงบปัจจุบัน):**
```bash
uv run python py-get-hdc.py 2570
```
หรือดับเบิลคลิกที่ไฟล์ `sync-2570.bat`

**Sync แยกปี 2569:**
```bash
uv run python py-get-hdc.py 2569
```
หรือดับเบิลคลิกที่ไฟล์ `sync-2569.bat`

**Sync ทั้งสองปีพร้อมกัน (2570 และ 2569):**
```bash
uv run python py-get-hdc.py
```
หรือดับเบิลคลิกที่ไฟล์ `sync-all.bat`

### 4. รันระบบตั้งเวลาอัตโนมัติ (Scheduler)
รันวันละ 2 รอบตามเวลา **09:09 น.** และ **16:16 น.**:
```bash
uv run python scheduler.py
```

## โครงสร้างโปรเจกต์
- `py-get-hdc.py`: สคริปต์หลักในการดึงข้อมูลและบันทึกฐานข้อมูล
- `scheduler.py`: ระบบตั้งเวลารันงานอัตโนมัติ
- `pyproject.toml`: การตั้งค่าโปรเจกต์และ dependencies
