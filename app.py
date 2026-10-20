import streamlit as st
import unicodedata

# 각 방의 문제, 정답, 힌트, 암호 숫자
ROOMS = [
    {
        "name": "자정의 무도회",
        "emoji": "👠 🕛 🎃",
        "question": "이 이모지가 나타내는 동화의 제목은?",
        "answers": ["신데렐라", "cinderella"],
        "hint": "유리 구두를 남기고 떠난 주인공이에요.",
        "digit": "3",
    },
    {
        "name": "얼어붙은 왕국",
        "emoji": "👭 ❄️ ⛄",
        "question": "이 이모지가 나타내는 애니메이션 영화의 제목은?",
        "answers": ["겨울왕국", "frozen"],
        "hint": "엘사와 안나가 등장해요.",
        "digit": "8",
    },
    {
        "name": "바닷속 비밀",
        "emoji": "🧽 🍍 🌊",
        "question": "바닷속 파인애플 집에 사는 이 캐릭터의 이름은?",
        "answers": ["스폰지밥", "네모바지 스폰지밥", "spongebob"],
        "hint": "노란색 몸에 네모난 바지를 입었어요.",
        "digit": "1",
    },
    {
        "name": "수상한 배달",
        "emoji": "⚫ 🍜 🥢",
        "question": "검은 춘장 소스를 비벼 먹는 이 면 요리의 이름은?",
        "answers": ["짜장면", "자장면"],
        "hint": "중국집에서 짬뽕과 함께 고민하는 메뉴예요.",
        "digit": "6",
    },
    {
        "name": "마법 학교",
        "emoji": "👓 ⚡ 🪄 🏰",
        "question": "번개 모양 흉터가 있는 이 주인공의 이름은?",
        "answers": ["해리포터", "harry potter"],
        "hint": "호그와트에 다니는 마법사예요.",
        "digit": "4",
    },
]


# 게임을 처음 상태로 되돌리는 함수
def reset_game():
    st.session_state.clear()
    st.session_state.update(
        stage=0,
        score=100,
        clues=[],
        hinted=[],
        mistakes=0,
        escaped=False,
        notice=None,
    )


# 띄어쓰기와 영문 대소문자 차이를 무시하는 함수
def normalize(text):
    return "".join(
        unicodedata.normalize("NFKC", text).split()
    ).casefold()


# 정답 제출 버튼을 눌렀을 때 실행하는 함수
def submit_answer():
    s = st.session_state
    answer = normalize(s.get(f"answer_{s.stage}", ""))

    if not answer:
        s.notice = (
            "warning",
            "답을 입력해 주세요. 빈 입력은 감점하지 않아요.",
        )
        return

    if s.stage < len(ROOMS):
        room = ROOMS[s.stage]
        correct = answer in [
            normalize(a) for a in room["answers"]
        ]
    else:
        correct = answer == "".join(s.clues)

    if not correct:
        s.score = max(0, s.score - 5)
        s.mistakes += 1
        s.notice = (
            "error",
            "정답이 아니에요. 다시 도전해 보세요! −5점",
        )
        return

    if s.stage < len(ROOMS):
        s.clues.append(room["digit"])
        s.stage += 1
        s.notice = (
            "success",
            f"문이 열렸어요! 암호 조각 [{room['digit']}] 획득!",
        )
    else:
        s.escaped = True
        s.notice = None


# 힌트는 방마다 처음 사용할 때만 감점
def show_hint():
    s = st.session_state

    if s.stage not in s.hinted:
        s.hinted.append(s.stage)
        s.score = max(0, s.score - 10)

    s.notice = None


# 웹페이지 설정
st.set_page_config(
    page_title="이모지 암호 방탈출",
    page_icon="🔐",
    layout="centered",
)

# 첫 접속일 때 게임 초기화
if "stage" not in st.session_state:
    reset_game()

s = st.session_state

st.title("🔐 이모지 암호 방탈출")
st.caption(
    "다섯 개의 문, 다섯 개의 숫자. 마지막 암호를 풀고 탈출하세요."
)

with st.expander("📖 처음이라면? 게임 방법"):
    st.write(
        "이모지를 보고 정답을 입력한 뒤 '정답 제출'을 누르세요. "
        "정답을 맞히면 숫자를 얻어요."
    )
    st.write(
        "시작 100점 · 오답 −5점 · "
        "힌트는 방마다 한 번 −10점 · 최저 0점"
    )
    st.write(
        "마지막에는 모은 숫자를 방 순서대로 입력하세요. "
        "가방 확인은 무료예요."
    )
    st.caption(
        "새로고침하거나 연결이 끊어지면 "
        "진행 상황이 초기화될 수 있어요."
    )

# 점수와 진행 상황
left, right = st.columns(2)
left.metric("현재 점수", f"{s.score}점")
right.metric("열린 문", f"{s.stage} / {len(ROOMS)}")

st.progress(
    (s.stage + int(s.escaped)) / (len(ROOMS) + 1)
)

# 정답 또는 오답 안내
if s.notice:
    kind, message = s.notice
    getattr(st, kind)(message)

# 탈출에 성공했을 때
if s.escaped:
    st.success("🎉 탈출 성공! 출구가 열렸습니다!")

    title = (
        "이모지 탐정"
        if s.score >= 90
        else "끈기 있는 수사관"
        if s.score >= 60
        else "포기하지 않는 탈출가"
    )

    st.subheader(f"🏆 {title}")
    st.write(
        f"최종 점수 **{s.score}/100점** · "
        f"오답 **{s.mistakes}회** · "
        f"힌트를 쓴 방 **{len(s.hinted)}개**"
    )

# 게임이 진행 중일 때
else:
    if s.stage < len(ROOMS):
        room = ROOMS[s.stage]

        st.subheader(
            f"🚪 {s.stage + 1}번 방 · {room['name']}"
        )
        st.markdown(
            "<div style='"
            "font-size:clamp(40px,9vw,64px);"
            "text-align:center;"
            "padding:24px 0;"
            f"'>{room['emoji']}</div>",
            unsafe_allow_html=True,
        )
        st.write(room["question"])
        label = "정답"

    else:
        st.subheader("🔒 마지막 출구")
        st.write(
            "가방에 모인 숫자를 "
            "**방을 통과한 순서대로** 이어 붙여 입력하세요."
        )
        label = "최종 암호"

    # 답 입력창과 제출 버튼
    with st.form(f"form_{s.stage}"):
        st.text_input(
            label,
            key=f"answer_{s.stage}",
            placeholder="여기에 입력하세요",
        )
        st.form_submit_button(
            "정답 제출"
            if s.stage < len(ROOMS)
            else "탈출하기",
            on_click=submit_answer,
            type="primary",
        )

    # 힌트 버튼
    if s.stage < len(ROOMS):
        used = s.stage in s.hinted

        st.button(
            "💡 힌트 사용 완료"
            if used
            else "💡 힌트 보기 (−10점)",
            key="hint",
            on_click=show_hint,
            disabled=used,
        )

        if used:
            st.info(ROOMS[s.stage]["hint"])

# 모은 암호 숫자 확인
with st.expander("🎒 암호 가방 — 무료로 확인"):
    st.write(
        " → ".join(s.clues)
        if s.clues
        else "아직 모은 숫자가 없어요. 첫 번째 문을 열어 보세요!"
    )

# 다시 시작 버튼
st.divider()

if s.escaped:
    st.button(
        "🔄 다시 시작",
        key="restart",
        on_click=reset_game,
    )
else:
    with st.expander("처음부터 다시 하기"):
        st.caption("현재 점수와 모은 숫자가 초기화됩니다.")
        st.button(
            "🔄 다시 시작",
            key="restart",
            on_click=reset_game,
        )
