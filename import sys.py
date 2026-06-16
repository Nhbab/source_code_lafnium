import sys
import re
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import QSize

# ==========================================
# 1. PARSER CORE (Phân tích cú pháp dạng QML)
# ==========================================
class MarkupParser:
    """Biến đổi chuỗi văn bản QML thành cấu trúc cây đối tượng Python."""
    @staticmethod
    def parse(code):
        # Xóa các dòng trống và khoảng trắng thừa ở đầu/cuối dòng
        lines = [line.strip() for line in code.strip().split('\n') if line.strip()]
        
        root_element = None
        current_element = None
        
        # Regex đơn giản để bắt cặp key: value hoặc Tên_Widget {
        block_pattern = re.compile(r"([A-Za-z0-9]+)\s*\{")
        prop_pattern = re.compile(r"([a-zA-Z_]+)\s*:\s*\"?([^\"]+)\"?")
        
        for line in lines:
            block_match = block_pattern.match(line)
            if block_match:
                element_type = block_match.group(1)
                new_el = {"type": element_type, "properties": {}, "children": []}
                if root_element is None:
                    root_element = new_el
                if current_element:
                    current_element["children"].append(new_el)
                current_element = new_el
                continue
                
            if line == "}":
                # Kết thúc một block (Ở phiên bản đơn giản này, ta giả định quay về root hoặc giữ nguyên)
                continue
                
            prop_match = prop_pattern.match(line)
            if prop_match and current_element:
                key = prop_match.group(1)
                val = prop_match.group(2)
                current_element["properties"][key] = val
                
        return root_element

# ==========================================
# 2. RUNTIME ENGINE (Trực quan hóa sang Qt)
# ==========================================
class PyQMLRuntime:
    """Đọc cây dữ liệu từ Parser và tạo ra UI Qt tương ứng."""
    def __init__(self):
        self.widgets_pool = [] # Giữ tham chiếu

    def build_ui(self, element_data):
        if not element_data:
            return None
            
        el_type = element_data["type"]
        props = element_data["properties"]
        
        # Ánh xạ tên Linh Kiện sang Qt Widget thực tế
        if el_type == "Window" or el_type == "Rectangle":
            widget = QWidget()
            # Áp dụng màu nền thông qua Qt Style Sheet giống đặc tính QML
            if "color" in props:
                widget.setStyleSheet(f"background-color: {props['color']}; border-radius: 4px;")
        elif el_type == "Button":
            widget = QPushButton()
            if "text" in props:
                widget.setText(props["text"])
        elif el_type == "Text":
            widget = QLabel()
            if "text" in props:
                widget.setText(props["text"])
            if "color" in props:
                widget.setStyleSheet(f"color: {props['color']}; font-weight: bold;")
        else:
            return None
            
        # Áp dụng các thuộc tính kích thước chung
        width = int(props.get("width", 200))
        height = int(props.get("height", 100))
        widget.setFixedSize(QSize(width, height))
        
        # Nếu linh kiện có chứa các linh kiện con bên trong
        if element_data["children"]:
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(5)
            for child_data in element_data["children"]:
                child_widget = self.build_ui(child_data)
                if child_widget:
                    layout.addWidget(child_widget)
                    
        return widget

# ==========================================
# 3. THỰC THI CHƯƠNG TRÌNH
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Đoạn mã Markup Language tùy chỉnh của bạn (Giống cú pháp QML của Qt)
    my_qml_code = """
    Window {
        width: 400
        height: 300
        color: "#2e2e2e"
        
        Text {
            text: "Chào mừng tới PyQML Engine!"
            color: "#ffffff"
            width: 350
            height: 40
        }
        
        Button {
            text: "Bấm vào tôi"
            width: 150
            height: 40
        }
        
        Rectangle {
            color: "#ff3366"
            width: 100
            height: 50
        }
    }
    """
    
    # Bước 1: Dịch mã nguồn thành cây dữ liệu cấu trúc
    ast_tree = MarkupParser.parse(my_qml_code)
    print("[AST LOG]:", ast_tree)
    
    # Bước 2: Chạy Runtime để sinh giao diện Qt nguyên bản
    runtime = PyQMLRuntime()
    main_window = runtime.build_ui(ast_tree)
    
    if main_window:
        main_window.setWindowTitle("PyQML Interpreter Engine")
        main_window.show()
        sys.exit(app.exec())
    else:
        print("[LỖI] Không thể biên dịch file markup.")
