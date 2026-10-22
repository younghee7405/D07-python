import json
import os
import urllib.error
import urllib.request

import streamlit as st

API_URL = "https://v6.exchangerate-api.com/v6/{key}/latest/{base}"

# 통화 코드 -> (이름, 카드 색상)
CURRENCIES = {
    "KRW": ("🇰🇷 대한민국 원", "#ff6b6b"),
    "USD": ("🇺🇸 미국 달러", "#4dabf7"),
    "EUR": ("🇪🇺 유로", "#845ef7"),
    "JPY": ("🇯🇵 일본 엔", "#f783ac"),
    "CNY": ("🇨🇳 중국 위안", "#ffa94d"),
    "GBP": ("🇬🇧 영국 파운드", "#38d9a9"),
    "AUD": ("🇦🇺 호주 달러", "#69db7c"),
    "CAD": ("🇨🇦 캐나다 달러", "#ff8787"),
    "CHF": ("🇨🇭 스위스 프랑", "#74c0fc"),
    "THB": ("🇹🇭 태국 바트", "#faa2c1"),
    "VND": ("🇻🇳 베트남 동", "#ffd43b"),
}
CARD_TARGETS = ["USD", "EUR", "JPY", "CNY", "GBP"]


def load_env(path=".env"):
    """같은 폴더의 .env 파일을 읽어 환경변수로 등록 (이미 있는 값은 유지)"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def get_default_api_key():
    """.env 또는 환경변수 EXCHANGERATE_API_KEY, 없으면 빈 문자열"""
    load_env()
    key = os.environ.get("EXCHANGERATE_API_KEY", "")
    if key.startswith("여기에"):
        key = ""  # 아직 채우지 않은 placeholder
    return key


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rates(api_key, base):
    """base 통화 기준 환율표 (1시간 캐시로 무료 요청 횟수 절약)"""
    with urllib.request.urlopen(API_URL.format(key=api_key, base=base), timeout=10) as res:
        return json.load(res)


def fmt(value):
    return f"{value:,.0f}" if abs(value) >= 100 else f"{value:,.4f}"


st.set_page_config(page_title="환율 계산기", page_icon="💱")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #fff1eb 0%, #e0f3ff 50%, #f3e8ff 100%); }
    .hero {
        background: linear-gradient(90deg, #ff6b6b, #ffa94d, #ffd43b, #69db7c, #4dabf7, #845ef7);
        color: white; padding: 22px; border-radius: 18px; text-align: center;
        font-size: 2rem; font-weight: 800; margin-bottom: 18px;
        text-shadow: 0 2px 6px rgba(0,0,0,.25);
    }
    .result {
        background: linear-gradient(135deg, #845ef7, #4dabf7); color: white;
        padding: 22px; border-radius: 18px; text-align: center; margin: 14px 0;
        box-shadow: 0 6px 18px rgba(132,94,247,.35);
    }
    .result .big { font-size: 2.2rem; font-weight: 800; }
    .card {
        color: white; padding: 14px; border-radius: 14px; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,.15); margin-bottom: 10px;
    }
    .card .code { font-size: 1.1rem; font-weight: 700; }
    .card .val { font-size: 1.3rem; font-weight: 800; }
    </style>
    <div class="hero">💱 환율 계산기</div>
    """,
    unsafe_allow_html=True,
)

api_key = get_default_api_key()
if not api_key:
    api_key = st.text_input("ExchangeRate API 키", type="password")

codes = list(CURRENCIES)
label = lambda c: f"{CURRENCIES[c][0]} ({c})"

amount = st.number_input("금액", min_value=0.0, value=1000.0, step=100.0)
col1, col2 = st.columns(2)
base = col1.selectbox("보내는 통화", codes, index=codes.index("USD"), format_func=label)
target = col2.selectbox("받는 통화", codes, index=codes.index("KRW"), format_func=label)

if st.button("계산하기", type="primary"):
    if not api_key:
        st.error("API 키가 없습니다.")
    else:
        try:
            with st.spinner("환율 불러오는 중..."):
                data = fetch_rates(api_key, base)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                st.error("API 키가 올바르지 않거나 비활성화되었습니다.")
            elif e.code == 429:
                st.error("요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.")
            else:
                st.error(f"요청 실패: HTTP {e.code}")
        except urllib.error.URLError as e:
            st.error(f"네트워크 오류: {e.reason}")
        else:
            if data.get("result") != "success":
                st.error(f"API 오류: {data.get('error-type', '알 수 없음')}")
            else:
                rates = data["conversion_rates"]
                st.markdown(
                    f"""
                    <div class="result">
                        <div>{fmt(amount)} {base} =</div>
                        <div class="big">{fmt(amount * rates[target])} {target}</div>
                        <div>1 {base} = {fmt(rates[target])} {target}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.subheader(f"{fmt(amount)} {base}는 다른 통화로?")
                others = [c for c in CARD_TARGETS if c != base and c in rates][:5]
                cols = st.columns(len(others))
                for col, c in zip(cols, others):
                    col.markdown(
                        f"""
                        <div class="card" style="background:{CURRENCIES[c][1]}">
                            <div class="code">{c}</div>
                            <div class="val">{fmt(amount * rates[c])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                st.caption(f"최근 업데이트: {data.get('time_last_update_utc', '-')}")
