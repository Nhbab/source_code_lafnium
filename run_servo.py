import os
import sys
import subprocess
from pathlib import Path

def run_isolated_servo():
    # --- ĐƯỜNG DẪN CẤU HÌNH G-STREAMER VÀ SERVO ---
    GSTREAMER_ROOT = Path(r"D:\gstreamer\1.0\msvc_x86_64")
    SERVO_EXE_DIR = Path(r".\target\release")
    SERVO_EXE_NAME = "servoshell.exe"
    DEFAULT_URL = "https://w3schools.com" # Video test trực tiếp
    
    gst_bin = GSTREAMER_ROOT / "bin"
    gst_plugins = GSTREAMER_ROOT / "lib" / "gstreamer-1.0"
    
    if not gst_bin.exists():
        print(f"[LỖI] Không tìm thấy thư mục GStreamer tại: {gst_bin}")
        print("[HƯỚNG DẪN] Hãy chắc chắn bạn đã cài đặt gói GStreamer MSVC (cả Runtime và Devel).")
        sys.exit(1)

    print("[INFO] Đang thiết lập môi trường Virtual Wrapper...")
    
    # Sao chép môi trường hệ thống hiện tại
    isolated_env = os.environ.copy()
    
    # 1. Ép Windows tìm file DLL gốc trong thư mục bin của GStreamer trước tiên
    isolated_env["PATH"] = f"{gst_bin};{isolated_env.get('PATH', '')}"
    
    # 2. Định tuyến tuyệt đối nơi chứa các plugin giải mã (avdec, gstplayback, gstapp...)
    isolated_env["GST_PLUGIN_PATH"] = str(gst_plugins)
    
    # 3. Ép dùng appsink để đẩy khung hình video mượt mà vào luồng đồ họa của Servo
    isolated_env["GST_VIDEO_SINK"] = "appsink"
    
    # 4. Bỏ qua các lỗi chặn chứng chỉ mạng SSL/TLS trên Windows gây xoay vòng vô tận
    isolated_env["GST_TLS_GIO_USE_SSL_CONTEXT"] = "0"
    isolated_env["GST_REGISTRY_DISABLE_WINDOW_REGISTRY"] = "1"
    
    # 5. Kích hoạt log mức 2 (Error/Warning) để theo dõi nếu video lỗi
    isolated_env["GST_DEBUG"] = "2,uridecodebin:4,decodebin:4,appsink:4"
    
    # Đăng ký DLL an toàn cho các phiên bản Python đời mới
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(str(gst_bin))
            os.add_dll_directory(str(SERVO_EXE_DIR.resolve()))
        except Exception as e:
            pass

    # Kiểm tra file chạy Servo đã được build chưa
    servo_path = SERVO_EXE_DIR / SERVO_EXE_NAME
    if not servo_path.exists():
        print(f"[LỖI] Không tìm thấy file chạy Servo tại: {servo_path}")
        print("[HƯỚNG DẪN] Bạn cần chạy lệnh './mach build --release' thành công trước.")
        sys.exit(1)
        
    target_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

    print(f"[LAUNCH] Khởi chạy Servo nạp luồng video: {target_url}")
    print("-" * 60)

    try:
        process = subprocess.Popen(
            [str(servo_path), target_url],
            env=isolated_env,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        process.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Đã đóng trình chạy Servo.")
        process.terminate()

if __name__ == "__main__":
    run_isolated_servo()
