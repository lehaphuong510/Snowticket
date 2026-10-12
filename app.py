import requests
import streamlit as st
import pandas as pd

# Thiết lập giao diện trang web
st.set_page_config(page_title="Thống kê vé", layout="centered")
st.title("📊 Bảng theo dõi số lượng vé bán ra")

# Headers và URL bóc tách từ lệnh cURL
API_URL = "https://api-v2.ticketbox.vn/event/api/v1/events/showings/41775904473808/seatmap"
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7",
    "content-type": "application/json",
    "origin": "https://ticketbox.vn",
    "referer": "https://ticketbox.vn/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
    "x-tb-access-token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJpZGVudGl0eS50aWNrZXRib3gudm4iLCJhdWQiOlsiYXBpLnRpY2tldGJveC52biJdLCJleHAiOjE3OTE4MTYwMjcsImlhdCI6MTc5MTgxNTkwNywiZGV2aWNlX2lkIjoiN2EyNjA3YjI3MWI5ZjU5YjliZTczYjNjOWNhMTU3ZmYiLCJ1c2VyX2lkIjozMzk4MzkzLCJlbWFpbCI6ImxlaGFwaHVvbmc1MTBAZ21haWwuY29tIiwibmFtZSI6IlBoxrDGoW5nIEzDqiIsInBob25lIjoiKzg0OTAzMTk5ODI1IiwicGxhdGZvcm0iOiJ3ZWIiLCJzZXNzaW9uX2lkIjoiNDI1NmZlYmUtYzlkYy00ZWVmLTllNDMtMzNlZGI3MmMyYmZlIiwia2luZCI6ImFjY2Vzc190b2tlbiJ9.bx5mR3jZrJwWuzoG6u50g4sM4q1AiIoGHriZupS2Mq_kDzarLD8rT5wPIOl-FhiP8P_Nc6BNCDLkH_zRX9wE8XIPr7wEzQouH4meCrU6uKQJZ2Tz0cs5skeAy6GTuszqETJp3XR_v1HOWEvXtaxHt12uYGcOLK0Jo7OwD09AWlP62xpzf8Sr5SMNZEoFDEKaXNjC_lpxCmgHI2ZkdvBwBiAm-SwdTF6BqknNJmtrrjPNF9d1JRby4m5kYtg_J21Qw6Cso-mLKJ_bH_JqL3o6a4glbya4sj-6pCSygXpNgLjMJgXe_GTH2LTXBh-SAM2ayW18NOSiJk23HIDYEtBu7g"
}

# Lấy dữ liệu (Cache trong 30 giây để tránh bị Ticketbox block IP do spam request)
@st.cache_data(ttl=30)
def fetch_ticket_data():
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return None

data = fetch_ticket_data()

if data:
    sections = data.get("result", {}).get("sections", [])
    stats = []
    
    for sec in sections:
        # Bỏ qua object vẽ sân khấu
        if sec.get("isStage"): 
            continue
            
        name = sec.get("name", "Unknown")
        # Ticketbox thường chứa danh sách ghế trong key 'seats' hoặc 'blocks'
        seats = sec.get("seats", []) 
        
        if seats:
            total = len(seats)
            # Thường status = 0 là ghế trống (đang mở bán), status = 1 hoặc 2 là đã bán/đang khóa
            sold = sum(1 for s in seats if s.get("status") != 0)
            stats.append({
                "Hạng Vé / Khu Vực": name, 
                "Tổng vé": total, 
                "Đã bán": sold, 
                "Còn trống": total - sold
            })

    if stats:
        df = pd.DataFrame(stats)
        
        # In 3 chỉ số tổng quan ở trên cùng
        col1, col2, col3 = st.columns(3)
        col1.metric("🎫 Tổng vé toàn rạp", df["Tổng vé"].sum())
        col2.metric("🔥 Tổng vé đã bán", df["Đã bán"].sum())
        col3.metric("✅ Còn trống", df["Còn trống"].sum())
        
        # In bảng chi tiết
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Đã gọi API thành công nhưng cấu trúc JSON không có key 'seats' ở cấp này.")
        # In raw JSON ra web để bạn tự soi lại cấu trúc key chính xác
        with st.expander("Xem cấu trúc JSON thực tế để debug"):
            st.json(sections[:2]) 

if st.button("🔄 Làm mới dữ liệu"):
    fetch_ticket_data.clear()
    st.rerun()
