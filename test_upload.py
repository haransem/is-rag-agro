#!/usr/bin/env python3
"""
Test script for document upload with new filename generation
"""
import requests
import os

# Server URL
BASE_URL = "http://localhost:8000"

# Create a test file
test_file_path = "/tmp/test_document.txt"
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write("""
การเกษตรยั่งยืนในประเทศไทย

การเกษตรยั่งยืนเป็นแนวทางการทำเกษตรที่ให้ความสำคัญต่อการรักษาสมดุลของระบบนิเวศ
โดยการใช้ทรัพยากรธรรมชาติอย่างมีประสิทธิภาพและไม่ทำลายสิ่งแวดล้อม

หลักการสำคัญของการเกษตรยั่งยืน:
1. การใช้ปุ่ยอินทรีย์แทนปุ่ยเคมี
2. การหมุนเวียนพืชปลูก
3. การจัดการศัตรูพืชด้วยวิธีธรรมชาติ
4. การอนุรักษ์ดินและน้ำ
5. การสร้างความหลากหลายทางชีวภาพ

ประโยชน์ของการเกษตรยั่งยืน:
- ลดต้นทุนการผลิต
- เพิ่มคุณภาพผลผลิต
- รักษาสิ่งแวดล้อม
- สร้างรายได้ที่มั่นคง

การเกษตรยั่งยืนจึงเป็นแนวทางที่สำคัญสำหรับการพัฒนาเกษตรกรรมของประเทศไทยในอนาคต
""")

def test_upload_document():
    """Test document upload with new filename system"""
    url = f"{BASE_URL}/api/v1/documents/upload"
    
    # Upload the test file
    with open(test_file_path, "rb") as f:
        files = {"file": ("test_document.txt", f, "text/plain")}
        response = requests.post(url, files=files)
    
    print(f"Upload response status: {response.status_code}")
    print(f"Upload response: {response.json()}")
    
    return response.status_code == 200

def test_multiple_uploads():
    """Test multiple uploads to see running number increment"""
    url = f"{BASE_URL}/api/v1/documents/upload"
    
    for i in range(3):
        # Create different content for each upload
        test_file = f"/tmp/test_doc_{i}.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(f"Test document number {i+1}\nContent for testing filename generation.")
        
        # Upload the file
        with open(test_file, "rb") as f:
            files = {"file": (f"test_doc_{i}.txt", f, "text/plain")}
            response = requests.post(url, files=files)
        
        print(f"Upload {i+1} - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Saved filename: {data.get('saved_filename', 'N/A')}")
            print(f"  Original filename: {data.get('original_filename', 'N/A')}")
        else:
            print(f"  Error: {response.text}")
        
        # Clean up
        os.remove(test_file)

if __name__ == "__main__":
    print("🧪 Testing new filename generation system...")
    print("=" * 50)
    
    print("1. Testing single upload...")
    success = test_upload_document()
    
    print("\n2. Testing multiple uploads (running number increment)...")
    test_multiple_uploads()
    
    # Clean up
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    
    print("\n✅ Test completed!")