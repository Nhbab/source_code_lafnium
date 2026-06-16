// Dẫn thẳng mã nguồn sang thư mục backend gstreamer có sẵn của bạn
#[cfg(feature = "media-gstreamer")]
pub mod backend {
    pub use gstreamer::*;
}
