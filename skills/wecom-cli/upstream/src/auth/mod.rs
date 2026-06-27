mod bot;
mod qrcode;

pub use bot::{Bot, clear_bot_info, get_bot_info, set_bot_info};
pub use qrcode::scan_qrcode_for_bot;
