import json
import os
import urllib.error
import urllib.parse
import urllib.request

import streamlit as st

API_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_CITY = "Seoul"


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
    """.env 또는 환경변수 OPENWEATHER_API_KEY, 없으면 빈 문자열"""
    load_env()
    key = os.environ.get("OPENWEATHER_API_KEY", "")
    if key.startswith("여기에"):
        key = ""  # 아직 채우지 않은 placeholder
    return key


def fetch_weather(api_key, city):
    params = urllib.parse.urlencode({
        "q": city,
        "appid": api_key,
        "units": "metric",   # 섭씨
        "lang": "kr",        # 날씨 설명 한국어
    })
    with urllib.request.urlopen(f"{API_URL}?{params}", timeout=10) as res:
        return json.load(res)


st.set_page_config(page_title="현재 날씨", page_icon="🌤️")
st.title("🌤️ 현재 날씨")

city = st.text_input("도시 (영문)", value=DEFAULT_CITY)
api_key = get_default_api_key()
if not api_key:
    api_key = st.text_input("OpenWeather API 키", type="password")

if st.button("날씨 조회", type="primary"):
    if not api_key:
        st.error("API 키가 없습니다.")
    elif not city.strip():
        st.error("도시 이름을 입력하세요.")
    else:
        try:
            with st.spinner("불러오는 중..."):
                data = fetch_weather(api_key, city.strip())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                st.error("API 키가 올바르지 않거나 아직 활성화되지 않았습니다. (새 키는 활성화까지 최대 몇 시간 걸릴 수 있어요)")
            elif e.code == 404:
                st.error(f"도시를 찾을 수 없습니다: {city}")
            else:
                st.error(f"요청 실패: HTTP {e.code}")
        except urllib.error.URLError as e:
            st.error(f"네트워크 오류: {e.reason}")
        else:
            main_info = data["main"]
            description = data["weather"][0]["description"]

            st.subheader(f"{data.get('name', city)} 현재 날씨")
            col1, col2, col3 = st.columns(3)
            col1.metric("기온", f"{main_info['temp']:.1f}°C")
            col2.metric("체감 온도", f"{main_info['feels_like']:.1f}°C")
            col3.metric("습도", f"{main_info['humidity']}%")
            st.info(f"날씨: {description}")
