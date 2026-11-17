import time
import subprocess
import os
import sys
from datetime import datetime, timedelta

# กำหนดเวลาที่ต้องการรัน 2 เวลาต่อวัน (24-hour format)
TARGET_TIMES = [
    (9, 9),    # รอบเช้า 09:09 น.
    (16, 16),  # รอบเย็น 16:16 น.
]

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
    times_str = ", ".join([f"{h:02d}:{m:02d}" for h, m in TARGET_TIMES])
    print(f"🎯 เป้าหมาย: รันทุกวันเวลา {times_str} น.")
    print("=" * 60)

    last_run_slot = None

    while True:
        now = datetime.now()
        current_hm = (now.hour, now.minute)
        
        # ตรวจสอบว่าเป็นเวลาที่กำหนดในรอบวันนี้หรือไม่
        if current_hm in TARGET_TIMES and last_run_slot != (now.date(), current_hm):
            print(f"\n⏰ ถึงเวลารันรอบ: {now.hour:02d}:{now.minute:02d} น.")
            run_job()
            last_run_slot = (now.date(), current_hm)
            
            # รอ 65 วินาทีเพื่อป้องกันการรันซ้ำในนาทีเดียวกัน
            print(f"💤 จบรอบ {now.hour:02d}:{now.minute:02d} น. กำลังรอรอบถัดไป...")
            time.sleep(65)
        else:
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 ปิดระบบ Scheduler")
