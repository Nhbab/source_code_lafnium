import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

# --- THÊM ĐOẠN NÀY ĐỂ SỬA LỖI PYLANCE / MISSING IMPORTS ---
# Tự động tìm và nạp thư mục chứa hệ thống mach nội bộ của Servo
current_file = Path(__file__).resolve()
servo_root = current_file.parents[2] # Đi ngược lên 2 cấp về thư mục gốc
mach_path = servo_root / "python" / "mach"
if mach_path.exists() and str(mach_path) not in sys.path:
    sys.path.insert(0, str(mach_path))
# ---------------------------------------------------------

# Bây giờ Pylance và Luồng chạy thực tế sẽ tìm thấy thư viện mà không báo lỗi
from mach.decorators import CommandProvider, Command


@CommandProvider
class ServoInstallerPackager:
    def __init__(self, context):
        self.context = context
        # Tự động định vị thư mục gốc của dự án Servo
        self.topdir = Path(context.topdir)

    @Command("package", category="package", description="Dong goi Servo va Driver Video thanh Bo cai dat chính thuc.")
    def package(self):
        host_os = platform.system().lower()
        dist_dir = self.topdir / "dist" / "servo-installer-source"
        os.makedirs(dist_dir, exist_ok=True)
        
        print(f"[MACH] Bat dau quy trinh dong goi luong video cho: {platform.system()}")
        
        # 1. Kích hoạt build Servo sang bản Release sạch
        print("[MACH] Dang bien dich Servo o che do Release...")
        subprocess.run([sys.executable, str(self.topdir / "mach"), "build", "--release"], check=True)

        # ==========================================
        # KỊCH BẢN WINDOWS: Tao file Setup Inno
        # ==========================================
        if host_os == "windows":
            exe_src = self.topdir / "target" / "release" / "servoshell.exe"
            shutil.copy(exe_src, dist_dir / "servoshell.exe")
            
            # Gom driver giải mã AV1/H264/VP9 vĩnh viễn
            gst_bin = Path(r"C:\gstreamer\1.0\msvc_x86_64\bin")
            gst_plugins = Path(r"C:\gstreamer\1.0\msvc_x86_64\lib\gstreamer-1.0")
            
            os.makedirs(dist_dir / "plugins", exist_ok=True)
            video_libs = ["gstdav1d.dll", "gstvideoconvert.dll", "gstplayback.dll", "gstapp.dll"]
            for lib in video_libs:
                shutil.copy(gst_plugins / lib, dist_dir / "plugins" / lib)
                
            shutil.copy(gst_bin / "dav1d.dll", dist_dir / "dav1d.dll")
            shutil.copy(gst_bin / "gstreamer-1.0-0.dll", dist_dir / "gstreamer-1.0-0.dll")
            
            # Gọi lệnh PyInstaller đóng gói ngầm nạp biến môi trường
            print("[MACH] Chay PyInstaller cho Windows...")
            # (Bạn có thể viết thêm logic gọi Inno Setup dòng lệnh tại đây)
            print(f"[MACH SUCCESS] Du lieu cai dat Windows da gom tai: {dist_dir}")

        # ==========================================
        # KỊCH BẢN LINUX: Tao file AppImage / DEB
        # ==========================================
        elif host_os == "linux":
            print("[MACH] Chay quy trinh trich xuat .so va tao .deb cho Linux...")
            # Chèn logic sao chép sang AppDir và gọi dpkg-deb như hướng dẫn trước
            
        # ==========================================
        # KỊCH BẢN MACOS: Tao file AppBundle .app
        # ==========================================
        elif host_os == "darwin":
            print("[MACH] Chay quy trinh cau truc hoa .app va thiet lap Info.plist cho Mac...")
            # Chèn logic sao chép sang Frameworks và gọi install_name_tool
