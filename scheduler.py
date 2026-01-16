import time
import subprocess
import os
import sys
from datetime import datetime, timedelta

# กำหนดเวลาที่ต้องการรัน (24-hour format)
TARGET_HOUR = 22
TARGET_MINUTE = 22

def run_job():
    """ฟังก์ชันสำหรับรันงาน"""
    print(f"\n🚀 เริ่มรันงานเวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        # ใช้ python ของ environment ปัจจุบันรัน script
        # เพื่อให้แน่ใจว่าใช้ dependencies เดียวกัน
        result = subprocess.run([sys.executable, "py-get-hdc.py"], capture_output=False, text=True)
        if result.returncode == 0:
            print("✅ งานเสร็จสมบูรณ์")
        else:
            print(f"❌ เกิดข้อผิดพลาด (Code: {result.returncode})")
    except Exception as e:
        print(f"❌ Error executing job: {e}")

def main():
    print("=" * 60)
    print(f"⏳ เริ่มต้นระบบ Scheduler")
    current_time = datetime.now()
    print(f"🕒 เวลาปัจจุบันของระบบ: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 เป้าหมาย: รันทุกวันเวลา {TARGET_HOUR:02d}:{TARGET_MINUTE:02d}")
    print("=" * 60)

    last_run_date = None

    # ตรวจสอบว่าเวลาที่กำหนดผ่านไปหรือยังสำหรับวันนี้
    target_time = current_time.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
    if current_time > target_time:
         print(f"⚠️ คำเตือน: เวลา {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} ของวันนี้ผ่านไปแล้ว (ระบบจะรันพรุ่งนี้)")
         print(f"   หรือคุณแก้ไข TARGET_HOUR/MINUTE บันทึกไฟล์ และรันสคริปต์ใหม่")

    while True:
        now = datetime.now()
        
        # แสดงสถานะแบบ Real-time (ทุก 1 นาที หรือเมื่อถึงเวลา)
        # ตรวจสอบว่าเป็นเวลาที่กำหนดหรือไม่ (ตรวจสอบช่วง 0-59 วินาทีของนาทีนั้น)
        if (now.hour == TARGET_HOUR and 
            now.minute == TARGET_MINUTE and 
            last_run_date != now.date()):
            
            run_job()
            last_run_date = now.date()
            
            # รอ 65 วินาทีเพื่อป้องกันการรันซ้ำ
            print("💤 รอรอบถัดไปในอีก 24 ชั่วโมง...")
            time.sleep(65)
        else:
            # Debug: แสดงเวลาทุกๆ 10 วินาที เพื่อให้รู้ว่า Script ทำงานอยู่
            # print(f"⏳ Waiting... Current time: {now.strftime('%H:%M:%S')}", end='\r')
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 ปิดระบบ Scheduler")
