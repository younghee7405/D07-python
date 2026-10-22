import json
import os
import urllib.error
import urllib.request

import streamlit as st

API = {
    "chat": "https://api.openai.com/v1/chat/completions",  # 🔌 OpenAI 챗봇
}
MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = "당신은 친절한 한국어 챗봇입니다. 간결하고 정확하게 답하세요."


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


def ask_openai(api_key, messages):
    body = json.dumps({"model": MODEL, "messages": messages}).encode("utf-8")
    req = urllib.request.Request(
        API["chat"],
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        data = json.load(res)
    return data["choices"][0]["message"]["content"]


load_env()
api_key = os.getenv("OPENAI_API_KEY", "")
if api_key.startswith("여기에"):
    api_key = ""  # 아직 채우지 않은 placeholder

st.set_page_config(page_title="챗봇", page_icon="💬")
st.title("💬 챗봇")
st.caption(f"모델: {MODEL}")

if not api_key:
    st.error(".env 에 OPENAI_API_KEY 가 없습니다.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("대화 지우기"):
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("생각 중..."):
                reply = ask_openai(
                    api_key,
                    [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                )
        except urllib.error.HTTPError as e:
            if e.code == 401:
                st.error("API 키가 올바르지 않습니다.")
            elif e.code == 429:
                st.error("요청이 너무 많거나 사용 한도를 넘었습니다.")
            else:
                st.error(f"요청 실패: HTTP {e.code}")
        except urllib.error.URLError as e:
            st.error(f"네트워크 오류: {e.reason}")
        except (KeyError, IndexError, json.JSONDecodeError):
            st.error("응답을 읽을 수 없습니다.")
        else:
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
