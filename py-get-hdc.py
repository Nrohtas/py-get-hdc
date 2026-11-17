"""
ดึงข้อมูลจาก MOPH Open Data API และบันทึกลงตาราง hdc แบบ upsert
"""

import os
import sys
import requests
import pymysql
from dotenv import load_dotenv
from datetime import datetime

# โหลด environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "43files"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# API configuration
API_URL = "https://opendata.moph.go.th/api/report_data"
DEFAULT_YEARS = ["2570", "2569"]


def fetch_data_from_api(year="2570"):
    """ดึงข้อมูลจาก MOPH Open Data API"""
    payload = {
        "tableName": "s_opd_all",
        "year": str(year),
        "province": "65",
        "type": "json"
    }
    print(f"🔄 กำลังดึงข้อมูลจาก API: {API_URL}")
    print(f"   Payload: {payload}")
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            timeout=60
        )
        response.raise_for_status()
        
        res_json = response.json()
        if isinstance(res_json, dict) and "data" in res_json:
            data = res_json["data"]
        elif isinstance(res_json, list):
            data = res_json
        else:
            data = []
            
        print(f"✅ ดึงข้อมูลสำเร็จ: {len(data)} รายการ (ปีงบ {year})")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลปี {year}: {e}")
        return None


def upsert_to_database(data):
    """บันทึกข้อมูลลงฐานข้อมูลแบบ upsert (INSERT ... ON DUPLICATE KEY UPDATE)"""
    if isinstance(data, dict) and "data" in data:
        data = data["data"]

    if not data:
        print("⚠️ ไม่มีข้อมูลสำหรับบันทึก")
        return 0, 0, 0
    
    print(f"🔄 กำลังบันทึกข้อมูล {len(data)} รายการลงฐานข้อมูล...")
    
    # SQL สำหรับ upsert
    # SQL สำหรับ upsert
    upsert_sql = """
        INSERT INTO hdc 
            (id, hospcode, areacode, date_com, b_year, target, result,
             result10, result11, result12, result01, result02, result03,
             result04, result05, result06, result07, result08, result09,
             status10, status11, status12, status01, status02, status03,
             status04, status05, status06, status07, status08, status09)
        VALUES 
            (%(id)s, %(hospcode)s, %(areacode)s, %(date_com)s, %(b_year)s, 
             %(target)s, %(result)s, 
             %(result10)s, %(result11)s, %(result12)s,
             %(result01)s, %(result02)s, %(result03)s,
             %(result04)s, %(result05)s, %(result06)s,
             %(result07)s, %(result08)s, %(result09)s,
             %(status10)s, %(status11)s, %(status12)s,
             %(status01)s, %(status02)s, %(status03)s,
             %(status04)s, %(status05)s, %(status06)s,
             %(status07)s, %(status08)s, %(status09)s)
        ON DUPLICATE KEY UPDATE
            hospcode = VALUES(hospcode),
            areacode = VALUES(areacode),
            date_com = VALUES(date_com),
            b_year = VALUES(b_year),
            target = VALUES(target),
            result = VALUES(result),
            result10 = VALUES(result10), status10 = VALUES(status10),
            result11 = VALUES(result11), status11 = VALUES(status11),
            result12 = VALUES(result12), status12 = VALUES(status12),
            result01 = VALUES(result01), status01 = VALUES(status01),
            result02 = VALUES(result02), status02 = VALUES(status02),
            result03 = VALUES(result03), status03 = VALUES(status03),
            result04 = VALUES(result04), status04 = VALUES(status04),
            result05 = VALUES(result05), status05 = VALUES(status05),
            result06 = VALUES(result06), status06 = VALUES(status06),
            result07 = VALUES(result07), status07 = VALUES(status07),
            result08 = VALUES(result08), status08 = VALUES(status08),
            result09 = VALUES(result09), status09 = VALUES(status09),
            d_update = CURRENT_TIMESTAMP
    """
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection:
            with connection.cursor() as cursor:
                inserted_count = 0
                updated_count = 0
                skipped_count = 0
                
                h_y_count = 0
                h_n_count = 0
                
                # คำนวณเดือนที่ต้องการนับ (เดือนปัจจุบัน - 1)
                # สูตร: (เดือนปัจจุบัน - 2) % 12 + 1 จะได้เดือนก่อนหน้า (1-12)
                # เช่น เดือน 1 (ม.ค.) -> (1-2)%12 + 1 = 12 (ธ.ค.)
                current_month = datetime.now().month
                prev_month = (current_month - 2) % 12 + 1
                target_count_month = f"{prev_month:02d}"
                print(f"🎯 นับจำนวน Status (Y/N) ของเดือน: {target_count_month}")
                
                # ดึง hostype_new จากตาราง hospital ทั้งหมดเก็บไว้ใน dict
                cursor.execute("SELECT hospcode, hostype_new FROM hospital")
                hospital_data = {row['hospcode']: row['hostype_new'] for row in cursor.fetchall()}
                print(f"📋 โหลดข้อมูล hospital (hostype_new): {len(hospital_data)} รายการ")
                
                # กำหนด threshold ตาม hostype_new
                def get_threshold(hostype_new):
                    """คืนค่า threshold ตาม hostype_new"""
                    if hostype_new in ('13', '18', '21'):
                        return 99
                    elif hostype_new in ('5', '12'):
                        return 9999
                    elif hostype_new in ('8', '11'):
                        return 499
                    elif hostype_new == '7':
                        return 4999
                    else:
                        # hostype_new อื่นๆ ไม่ต้องคำนวณ status
                        return None
                
                # Helper function คำนวณ status ตาม threshold
                def calc_status(val, threshold):
                    """คำนวณ status: Y ถ้า val > threshold, N ถ้า val <= threshold"""
                    if threshold is None:
                        return None  # ไม่คำนวณ
                    try:
                        val_int = int(val) if val else 0
                        return 'Y' if val_int > threshold else 'N'
                    except (ValueError, TypeError):
                        return 'N'
                
                for record in data:
                    hospcode = record.get('hospcode')
                    
                    # ดึง hostype_new จาก dict
                    hostype_new = hospital_data.get(hospcode)
                    
                    # ถ้าไม่พบ hospital หรือ hostype_new ไม่อยู่ในกลุ่มที่กำหนด ให้ข้าม
                    threshold = get_threshold(hostype_new) if hostype_new else None
                    
                    if threshold is None:
                        print(f"      ⚠️ Skip: hospcode={hospcode}, hostype_new={hostype_new}")
                        skipped_count += 1
                        continue  # ข้าม record นี้
                    
                    # สร้าง unique id จาก hospcode + b_year
                    unique_id = f"{hospcode}_{record.get('b_year')}"

                    # เตรียมค่า result
                    results = {
                        '10': record.get("result10", 0), '11': record.get("result11", 0), '12': record.get("result12", 0),
                        '01': record.get("result01", 0), '02': record.get("result02", 0), '03': record.get("result03", 0),
                        '04': record.get("result04", 0), '05': record.get("result05", 0), '06': record.get("result06", 0),
                        '07': record.get("result07", 0), '08': record.get("result08", 0), '09': record.get("result09", 0)
                    }
                    
                    # ตรวจสอบว่ามีข้อมูลก่อนหรือไม่
                    cursor.execute(
                        "SELECT id FROM hdc WHERE id = %s",
                        (unique_id,)
                    )
                    exists = cursor.fetchone()
                    
                    # Parameters dict
                    params = {
                        "id": unique_id,
                        "hospcode": hospcode,
                        "areacode": record.get("areacode"),
                        "date_com": record.get("date_com"),
                        "b_year": record.get("b_year"),
                        "target": record.get("target", 0),
                        "result": record.get("result", 0)
                    }
                    
                    # เพิ่ม resultXX และ statusXX ลงใน params
                    for month, val in results.items():
                        params[f"result{month}"] = val
                        status = calc_status(val, threshold)
                        params[f"status{month}"] = status
                        
                        # นับจำนวน Y/N เฉพาะเดือนที่กำหนด
                        if month == target_count_month:
                            if status == 'Y':
                                h_y_count += 1
                            elif status == 'N':
                                h_n_count += 1

                    # Execute upsert
                    cursor.execute(upsert_sql, params)
                    
                    if exists:
                        updated_count += 1
                    else:
                        inserted_count += 1
                
            connection.commit()
            
        print(f"✅ บันทึกข้อมูลสำเร็จ!")
        print(f"   📥 เพิ่มใหม่: {inserted_count} รายการ")
        print(f"   🔄 อัปเดต: {updated_count} รายการ")
        print(f"   ⏭️ ข้าม (hostype_new ไม่ตรงเงื่อนไข): {skipped_count} รายการ")
        return inserted_count + updated_count, h_y_count, h_n_count
        
    except pymysql.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึกฐานข้อมูล: {e}")
        return 0, 0, 0


def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("📊 HDC Data Fetcher (43files)")
    print(f"🕐 เวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    target_years = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_YEARS
    print(f"🎯 ปีงบประมาณที่จะ sync: {', '.join(target_years)}")
    
    grand_total = 0
    for year in target_years:
        print("-" * 50)
        print(f"📌 กำลังประมวลผลปีงบประมาณ: {year}")
        data = fetch_data_from_api(year=year)
        
        if data:
            total, h_y, h_n = upsert_to_database(data)
            grand_total += total
            if total > 0:
                print(f"🎉 เสร็จสิ้นปี {year}! บันทึกข้อมูล {total} รายการ")
                log_api_run(year, len(data), h_y, h_n)
            else:
                print(f"⚠️ ไม่สามารถบันทึกข้อมูลปี {year} ได้")
        else:
            print(f"⚠️ ไม่พบข้อมูลของปี {year} จาก API")
            
    print("=" * 60)
    print(f"🏁 สรุปการทำงาน: บันทึกข้อมูลรวมทั้งหมด {grand_total} รายการ")
    print("=" * 60)

def create_log_table_if_not_exists(connection):
    """สร้างตาราง hdc_api ถ้ายังไม่มี และเพิ่มคอลัมน์ b_year ถ้ายังไม่มี"""
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hdc_api (
                api_id INT AUTO_INCREMENT PRIMARY KEY,
                b_year VARCHAR(4) DEFAULT NULL COMMENT 'ปีงบประมาณ',
                h_count INT COMMENT 'จำนวน hospcode',
                h_y INT DEFAULT 0 COMMENT 'จำนวน status Y',
                h_n INT DEFAULT 0 COMMENT 'จำนวน status N',
                d_update DATETIME COMMENT 'วันเวลาที่บันทึก'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("SHOW COLUMNS FROM hdc_api LIKE 'b_year'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE hdc_api ADD COLUMN b_year VARCHAR(4) DEFAULT NULL AFTER api_id")
    connection.commit()

def log_api_run(year, h_count, h_y, h_n):
    """บันทึก Log การทำงานลงตาราง hdc_api"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection:
            create_log_table_if_not_exists(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO hdc_api (b_year, h_count, h_y, h_n, d_update) VALUES (%s, %s, %s, %s, %s)",
                    (str(year), h_count, h_y, h_n, datetime.now())
                )
            connection.commit()
            print(f"📝 บันทึก Log สำเร็จ: year={year}, h_count={h_count}, h_y={h_y}, h_n={h_n}")
    except pymysql.Error as e:
        print(f"❌ ไม่สามารถบันทึก Log ได้: {e}")


if __name__ == "__main__":
    main()
