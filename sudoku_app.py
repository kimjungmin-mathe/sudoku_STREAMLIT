
import streamlit as st
import pandas as pd
import random
import time
import os

AVal = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    [4, 5, 6, 7, 8, 9, 1, 2, 3],
    [7, 8, 9, 1, 2, 3, 4, 5, 6],
    [2, 3, 1, 8, 9, 7, 5, 6, 4],
    [5, 6, 4, 2, 3, 1, 8, 9, 7],
    [8, 9, 7, 5, 6, 4, 2, 3, 1],
    [3, 1, 2, 6, 4, 5, 9, 7, 8],
    [6, 4, 5, 9, 7, 8, 3, 1, 2],
    [9, 7, 8, 3, 1, 2, 6, 4, 5]
]

RANK_FILE = "ranking.csv"


@st.cache_data
def load_ranking():
    if os.path.exists(RANK_FILE):
        return pd.read_csv(RANK_FILE)
    return pd.DataFrame(
        columns=["참가자", "기록(초)", "p", "날짜"]
    )


def shuffle(p):
    random19 = list(range(1, 10))
    random.shuffle(random19)

    answer = []
    board = []
    fixed = []

    for i in range(9):
        a_row = []
        b_row = []
        f_row = []

        for j in range(9):
            v = str(random19[AVal[i][j] - 1])
            a_row.append(v)

            if random.random() > p:
                b_row.append("")
                f_row.append(False)
            else:
                b_row.append(v)
                f_row.append(True)

        answer.append(a_row)
        board.append(b_row)
        fixed.append(f_row)

    st.session_state.answer = answer
    st.session_state.board = board
    st.session_state.fixed = fixed
    st.session_state.start = time.time()
    st.session_state.finish = False
    st.session_state.record = 0
    st.session_state.selected = None
    st.session_state.game_p = p
    st.session_state.msg = "새 게임 시작! 칸을 클릭하세요."


def select_cell(i, j):
    if not st.session_state.finish:
        if not st.session_state.fixed[i][j]:
            st.session_state.selected = (i, j)


def input_number(num):
    if st.session_state.finish:
        st.session_state.msg = "이미 끝난 게임입니다."
        return

    selected = st.session_state.selected

    if selected is None:
        st.session_state.msg = "먼저 스도쿠 판에서 칸을 선택하세요."
        return

    i, j = selected

    if st.session_state.fixed[i][j]:
        st.session_state.msg = "주어진 숫자는 바꿀 수 없습니다."
        return

    if num == "지우기":
        st.session_state.board[i][j] = ""
        st.session_state.msg = (
            f"{i + 1}행 {j + 1}열을 지웠습니다."
        )
    else:
        st.session_state.board[i][j] = num

        if num == st.session_state.answer[i][j]:
            result = "맞음"
        else:
            result = "틀림"

        st.session_state.msg = (
            f"{i + 1}행 {j + 1}열 = {num} ({result})"
        )


def complete_test(A):
    for i in range(9):
        for j in range(9):
            if A[i][j] == "":
                return "아직 빈칸이 있습니다."

    for i in range(9):
        if len(set(A[i])) != 9:
            return f"{i + 1}행 오류"

    for j in range(9):
        temp = [A[i][j] for i in range(9)]
        if len(set(temp)) != 9:
            return f"{j + 1}열 오류"

    for i in [0, 3, 6]:
        for j in [0, 3, 6]:
            temp = []

            for r in range(i, i + 3):
                for c in range(j, j + 3):
                    temp.append(A[r][c])

            if len(set(temp)) != 9:
                return f"3×3 영역 ({i + 1}, {j + 1}) 오류"

    return ""


def finish_game(player):
    if st.session_state.finish:
        st.session_state.msg = "이미 끝난 게임입니다."
        return

    err = complete_test(st.session_state.board)

    if err != "":
        st.session_state.msg = err
        return

    record = round(time.time() - st.session_state.start, 1)
    st.session_state.finish = True
    st.session_state.record = record

    new = pd.DataFrame(
        [[
            player,
            record,
            st.session_state.game_p,
            time.strftime("%Y-%m-%d %H:%M")
        ]],
        columns=["참가자", "기록(초)", "p", "날짜"]
    )

    old = load_ranking()
    df = pd.concat([old, new], ignore_index=True)
    df.to_csv(RANK_FILE, index=False)

    st.cache_data.clear()

    rank = len(df[df["기록(초)"] < record]) + 1

    st.session_state.msg = (
        f"!!! ~~~Congratulation~~~ !!! "
        f"{player} 기록 {record}초, {rank}등"
    )


# -------------------------
# 사이드바
# -------------------------

st.sidebar.title("Sudoku")

players = [f"참가자 {n}" for n in range(1, 21)]

player = st.sidebar.selectbox(
    "참가자를 선택하세요",
    players
)

p = st.sidebar.slider(
    "숫자가 보일 확률",
    0.3, 0.9, 0.7
)

if "board" not in st.session_state:
    shuffle(p)

if st.sidebar.button("Shuffle"):
    shuffle(p)


# -------------------------
# 메인 화면
# -------------------------

st.header("Sudoku 게임")

tab1, tab2 = st.tabs(["게임", "랭킹"])

with tab1:

    col1, col2 = st.columns([3, 2])

    # -------------------------
    # 클릭 가능한 스도쿠 판
    # -------------------------

    with col1:
        st.subheader("스도쿠 판")

        for i in range(9):
            cols = st.columns(9, gap="small")

            for j in range(9):
                value = st.session_state.board[i][j]

                if value == "":
                    label = "·"
                else:
                    label = value

                selected = (
                    st.session_state.selected == (i, j)
                )

                fixed = st.session_state.fixed[i][j]

                with cols[j]:
                    st.button(
                        label,
                        key=f"cell_{i}_{j}",
                        use_container_width=True,
                        type=(
                            "primary"
                            if selected
                            else "secondary"
                        ),
                        disabled=(
                            fixed or st.session_state.finish
                        ),
                        on_click=select_cell,
                        args=(i, j)
                    )

        st.caption(
            "빈칸을 클릭한 뒤 오른쪽 숫자 버튼을 누르세요."
        )

    # -------------------------
    # 숫자 입력
    # -------------------------

    with col2:
        st.subheader("숫자 입력")

        selected = st.session_state.selected

        if selected is None:
            st.info("입력할 칸을 클릭하세요.")
        else:
            i, j = selected
            st.info(
                f"선택한 칸: {i + 1}행 {j + 1}열"
            )

        for start_num in [1, 4, 7]:
            number_cols = st.columns(3)

            for offset in range(3):
                num = str(start_num + offset)

                with number_cols[offset]:
                    st.button(
                        num,
                        key=f"num_{num}",
                        use_container_width=True,
                        disabled=st.session_state.finish,
                        on_click=input_number,
                        args=(num,)
                    )

        st.button(
            "지우기",
            key="erase",
            use_container_width=True,
            disabled=st.session_state.finish,
            on_click=input_number,
            args=("지우기",)
        )

        st.divider()

        st.button(
            "Finish",
            use_container_width=True,
            on_click=finish_game,
            args=(player,)
        )

        st.write(st.session_state.msg)

        @st.fragment
        def timer():
            st.button("시간 확인")

            if st.session_state.finish:
                st.write(
                    "완료 기록:",
                    st.session_state.record,
                    "초"
                )
            else:
                elapsed = int(
                    time.time() - st.session_state.start
                )
                st.write("경과 시간:", elapsed, "초")

        timer()


# -------------------------
# 랭킹
# -------------------------

with tab2:
    df = load_ranking()

    if len(df) == 0:
        st.write("아직 기록이 없습니다.")

    else:
        st.subheader("전체 순위 TOP 10")

        df = df.sort_values(
            "기록(초)"
        ).reset_index(drop=True)

        df.index = df.index + 1

        st.table(df.head(10))

        my = df[
            df["참가자"] == player
        ].sort_values("날짜").reset_index(drop=True)

        if len(my) > 0:
            st.subheader(player + " 기록 변화")

            my["회차"] = my.index + 1

            st.line_chart(
                my,
                x="회차",
                y="기록(초)"
            )
