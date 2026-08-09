import sys
from unittest.mock import MagicMock

# --- TIỂU XẢO: Khóa mõm toàn bộ các thư viện đồ thị bị hỏng của vnstock3 ---
mock_obj = MagicMock()
sys.modules['vnstock_ezchart'] = mock_obj
sys.modules['vnstock_ezchart.mplot'] = mock_obj
sys.modules['vnstock_ezchart.static'] = mock_obj
sys.modules['vnstock_ezchart.static.chart'] = mock_obj
sys.modules['IPython'] = mock_obj
sys.modules['IPython.display'] = mock_obj
sys.modules['squarify'] = mock_obj
sys.modules['wordcloud'] = mock_obj
# -------------------------------------------------------------------------

import os
import time
import requests
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta

# Bây giờ gọi vnstock3 sẽ không bị vướng lỗi đồ thị nữa
from vnstock3.explorer.tcbs.quote import Quote

# 1. Khai báo các khóa bảo mật
GEMINI_KEY = os.environ.get("AQ.Ab8RN6IsgDTXPD6d6JmzPo9NBvjfDE-SGcZUHHliYbdCdgqH5A")
TELEGRAM_TOKEN = os.environ.get("8849020001:AAEjRXt00WK64wMxVO9kV_xL3ymmzU3Tr8E")
TELEGRAM_CHAT_ID = os.environ.get("6078316051")

def get_all_symbols():
    """Danh sách Top 80 cổ phiếu thanh khoản và tiềm năng nhất thị trường (Chống khóa IP, tối ưu tốc độ)"""
    return [
        "SSI", "VND", "VCI", "HCM", "SHS", "VIX", "MBS", "FTS", "BSI", "CTS",
        "HPG", "HSG", "NKG", "SMC", "VGS",
        "VCB", "BID", "CTG", "TCB", "MBB", "VPB", "STB", "ACB", "HDB", "SHB", "VIB", "LPB", "MSB", "OCB", "EIB",
        "VHM", "VIC", "VRE", "NVL", "DIG", "DXG", "PDR", "KDH", "NLG", "CEO", "CII", "HDG",
        "KBC", "IDC", "SZC", "VGC", "VCG", "LCG", "HHV", "CTD", "HBC", "FCN",
        "MWG", "PNJ", "MSN", "VNM", "SAB", "DGW", "FRT", "PET",
        "FPT", "GVR", "DGC", "CSV", "REE", "POW", "GAS", "PLX", "PVD", "PVS", "BSR",
        "GMD", "HAH", "VHC", "ANV", "ASM", "IDI", "GIL", "TNG", "VGT", "PC1", "BCG"
    ]

def scan_full_market():
    """Quét dữ liệu giá/volume của toàn bộ thị trường và lọc thô bằng tiêu chí Kỹ thuật"""
    all_symbols = get_all_symbols()
    qualified_stocks = []

    for symbol in all_symbols:
        try:
            # Nghỉ 3.5 giây trước khi quét mã tiếp theo để lách giới hạn 20 lần/phút
            time.sleep(3.5)

            today = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            df = Quote(symbol).history(start=start_date, end=today)

            # Căn tối thiểu 50 phiên dữ liệu để tính các đường MA
            if len(df) < 50:
                continue

            # Tính toán các chỉ báo cơ bản
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA50'] = df['close'].rolling(window=50).mean()
            df['Vol_MA20'] = df['volume'].rolling(window=20).mean()

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # Bộ lọc điều kiện cần (Lọc thô):
            cond_vol = latest['volume'] > 100000
            cond_trend = (latest['close'] >= latest['MA10']) and (latest['close'] >= latest['MA50'])
            cond_breakout_or_tight = (latest['volume'] >= 1.2 * latest['Vol_MA20']) or (abs(latest['close'] - prev['close'])/prev['close'] < 0.015)

            if cond_vol and cond_trend and cond_breakout_or_tight:
                qualified_stocks.append({
                    "ticker": symbol,
                    "price": float(latest['close']),
                    "prev_price": float(prev['close']),
                    "volume": int(latest['volume']),
                    "vol_ma20": int(latest['Vol_MA20']),
                    "ma10": float(latest['MA10']),
                    "ma50": float(latest['MA50'])
                })
        except Exception:
            continue

    print(f"Số mã đạt tiêu chí lọc thô: {len(qualified_stocks)}")
    return qualified_stocks

for symbol in all_symbols:
        try:
            # Nghỉ 3.5 giây trước khi quét mã tiếp theo để lách giới hạn 20 lần/phút
            time.sleep(3.5)

            today = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            df = Quote(symbol).history(start=start_date, end=today)

            # Căn tối thiểu 50 phiên dữ liệu để tính các đường MA
            if len(df) < 50:
                continue

            # Tính toán các chỉ báo cơ bản
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA50'] = df['close'].rolling(window=50).mean()
            df['Vol_MA20'] = df['volume'].rolling(window=20).mean()

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            cond_vol = latest['volume'] > 100000
            cond_trend = (latest['close'] >= latest['MA10']) and (latest['close'] >= latest['MA50'])
            cond_breakout_or_tight = (latest['volume'] >= 1.2 * latest['Vol_MA20']) or (abs(latest['close'] - prev['close']) / prev['close'] < 0.015)

            if cond_vol and cond_trend and cond_breakout_or_tight:
            qualified_stocks.append({
                "ticker": symbol,
                "price": float(latest['close']),
                "prev_price": float(prev['close']),
                "volume": int(latest['volume']),
                "vol_ma20": int(latest['Vol_MA20']),
                "ma10": float(latest['MA10']),
                "ma50": float(latest['MA50'])
            })
    except Exception:
        continue

print(f"Số mã đạt tiêu chí lọc thô: {len(qualified_stocks)}")
return qualified_stocks
def analyze_and_select_top10(market_data):
    """Gửi dữ liệu đã lọc thô sang Gemini để chọn ra TOP 10 mã VSA/Wyckoff tốt nhất"""
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f"""
    BẠN LÀ CHUYÊN GIA VSA / WYCKOFF HÀNG ĐẦU.
    Dưới đây là danh sách các cổ phiếu đã qua bộ lọc kỹ thuật ban đầu:
    {market_data}

    NHIỆM VỤ CỦA BẠN:
    1. Phân tích dữ liệu kỹ thuật và chọn ra ĐÚNG 10 MÃ CỔ PHIẾU XUẤT SẮC NHẤT thỏa mãn:
       - Tín hiệu Breakout bứt phá nền giá hoặc Siết nền giá biến động thu hẹp (VCP).
       - Tín hiệu Dòng tiền tổ chức tham gia (Volume Spike / Cạn cung VSA).
    2. Với mỗi mã, hãy trình bày:
       - Giá Hiện Tại
       - Vùng Mua (Entry)
       - Công thức & Giá Cắt Lỗ (SL): Giá SL = Giá Hiện Tại x 0.94 (Cắt lỗ 6%)
       - Nhận định ngắn gọn về Mẫu hình & Dòng tiền VSA.
    3. Định dạng đẹp mắt dưới dạng văn bản báo cáo Telegram.
    """

    response = model.generate_content(prompt)
    return response.text

def send_telegram(text):
    """Gửi báo cáo kết quả về ứng dụng Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    market_data = scan_full_market()
    report = analyze_and_select_top10(market_data)
    send_telegram(report)
