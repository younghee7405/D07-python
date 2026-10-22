import random
import tkinter as tk
from datetime import datetime

SETS = 5
NUMBERS_PER_SET = 6


def ball_color(n):
    """번호 구간별 공 색상 (동행복권 기준)"""
    if n <= 10:
        return "#FBC400", "black"   # 노랑
    if n <= 20:
        return "#69C8F2", "black"   # 파랑
    if n <= 30:
        return "#FF7272", "white"   # 빨강
    if n <= 40:
        return "#AAAAAA", "white"   # 회색
    return "#B0D840", "black"       # 초록


def generate():
    return [sorted(random.sample(range(1, 46), NUMBERS_PER_SET)) for _ in range(SETS)]


def on_click():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_label.config(text=f"추첨 일시: {now}")

    for row, numbers in zip(ball_rows, generate()):
        for lbl, n in zip(row, numbers):
            bg, fg = ball_color(n)
            lbl.config(text=str(n), bg=bg, fg=fg)


root = tk.Tk()
root.title("로또 번호 생성기")
root.resizable(False, False)

tk.Label(root, text="로또 번호 생성기", font=("맑은 고딕", 18, "bold")).pack(pady=(15, 5))

date_label = tk.Label(root, text=f"오늘 날짜: {datetime.now():%Y-%m-%d}", font=("맑은 고딕", 11))
date_label.pack()

frame = tk.Frame(root)
frame.pack(padx=20, pady=15)

ball_rows = []
for i in range(SETS):
    tk.Label(frame, text=f"{chr(65 + i)}", font=("맑은 고딕", 12, "bold")).grid(row=i, column=0, padx=8)
    row = []
    for j in range(NUMBERS_PER_SET):
        lbl = tk.Label(frame, text="-", width=4, height=2, bg="#EEEEEE",
                       font=("맑은 고딕", 12, "bold"), relief="groove")
        lbl.grid(row=i, column=j + 1, padx=3, pady=4)
        row.append(lbl)
    ball_rows.append(row)

tk.Button(root, text="번호 생성", command=on_click, font=("맑은 고딕", 13, "bold"),
          bg="#4A6CF7", fg="white", padx=20, pady=6).pack(pady=(0, 15))

root.mainloop()
