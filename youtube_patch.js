fn IndexedDB(&self) -> DomRoot<IDBFactory> {
    let current_url = self.globalscope.api_base_url().to_string();

    if current_url.contains("youtube.com") {
        println!("[SERVO PATCH] YouTube tracked. Injecting youtube_patch.js from root path...");
        
        // ─── ĐOẠN CODE ĐỌC VÀ ÉP THỰC THI FILE JAVASCRIPT CỤC BỘ ───
        if let Ok(js_content) = std::fs::read_to_string("./youtube_patch.js") {
            // Thực thi chuỗi mã lệnh JS trực tiếp vào ngữ cảnh chạy của trang web hiện tại
            let cx = self.get_cx();
            let _ = self.globalscope.evaluate_js_script(&js_content, cx);
        } else {
            println!("[SERVO WARNING] Khong tim thay file ./youtube_patch.js o thu muc goc!");
        }
        // ──────────────────────────────────────────────────────────
    }

    IDBFactory::new(&self.globalscope, CanGc::deprecated_note())
}
