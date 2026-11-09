import streamlit as st
import pandas as pd
import random
import time
import os

AVal = [[1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 1, 8, 9, 7, 5, 6, 4],
        [5, 6, 4, 2, 3, 1, 8, 9, 7],
        [8, 9, 7, 5, 6, 4, 2, 3, 1],
        [3, 1, 2, 6, 4, 5, 9, 7, 8],
        [6, 4, 5, 9, 7, 8, 3, 1, 2],
        [9, 7, 8, 3, 1, 2, 6, 4, 5]]

RANK_FILE = "ranking.csv"


@st.cache_data()
def load_ranking():
    if os.path.exists(RANK_FILE):
        return pd.read_csv(RANK_FILE)
    return pd.DataFrame(columns=["참가자", "기록(초)", "p", "날짜"])


def shuffle(p):
    random19 = list(range(1, 10))
    random.shuffle(random19)
    answer = []
    board = []
    fixed = []
    for i in range(0, 9):
        a_row = []
        b_row = []
        f_row = []
        for j in range(0, 9):
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
    st.session_state.msg = "새 게임 시작! 칸을 고르고 숫자를 입력하세요."


def complete_test(A):
    for i in range(0, 9):
        for j in range(0, 9):
            if A[i][j] == "":
                return "아직 빈칸이 있습니다."

    for i in range(0, 9):
        temp = []
        for j in range(0, 9):
            temp.append(A[i][j])
        if len(set(temp)) != 9:
            return str(i + 1) + "'th row Error"

    for j in range(0, 9):
        temp = []
        for i in range(0, 9):
            temp.append(A[i][j])
        if len(set(temp)) != 9:
            return str(j + 1) + "'th column Error"

    index = [0, 3, 6]
    for i in index:
        for j in index:
            temp = []
            for k in range(0, 3):
                temp.append(A[i][j + k])
                temp.append(A[i + 1][j + k])
                temp.append(A[i + 2][j + k])
            if len(set(temp)) != 9:
                return str(i) + ", " + str(j) + "'th 3*3 matrix Error"
    return ""


st.sidebar.title("Sudoku")
players = []
for n in range(1, 21):
    players.append("참가자 " + str(n))
player = st.sidebar.selectbox("참가자를 선택하세요", players)
p = st.sidebar.slider("숫자가 보일 확률", 0.3, 0.9, 0.7)

if "board" not in st.session_state:
    shuffle(p)

if st.sidebar.button("Shuffle"):
    shuffle(p)

st.header("Sudoku 게임")
tab1, tab2 = st.tabs(["게임", "랭킹"])

with tab1:
    col1, col2 = st.columns([3, 2])

    with col2:
        st.subheader("입력")
        row = st.selectbox("행", list(range(1, 10)))
        col = st.selectbox("열", list(range(1, 10)))
        num = st.selectbox("숫자", ["1", "2", "3", "4", "5", "6", "7", "8", "9", "지우기"])

        if st.button("입력"):
            i = row - 1
            j = col - 1
            if st.session_state.finish:
                st.session_state.msg = "이미 끝난 게임입니다. Shuffle을 눌러 새 게임을 시작하세요."
            elif st.session_state.fixed[i][j]:
                st.session_state.msg = "처음부터 주어진 칸은 바꿀 수 없습니다."
            elif num == "지우기":
                st.session_state.board[i][j] = ""
                st.session_state.msg = str(row) + "행 " + str(col) + "열을 지웠습니다."
            else:
                st.session_state.board[i][j] = num
                if num == st.session_state.answer[i][j]:
                    st.session_state.msg = str(row) + "행 " + str(col) + "열 = " + num + "  (맞음)"
                else:
                    st.session_state.msg = str(row) + "행 " + str(col) + "열 = " + num + "  (틀림)"

        if st.button("Finish"):
            if st.session_state.finish:
                st.session_state.msg = "이미 끝난 게임입니다. Shuffle을 눌러 새 게임을 시작하세요."
            else:
                err = complete_test(st.session_state.board)
                if err != "":
                    st.session_state.msg = err
                else:
                    record = round(time.time() - st.session_state.start, 1)
                    st.session_state.finish = True
                    st.session_state.record = record
                    new = pd.DataFrame([[player, record, p, time.strftime("%Y-%m-%d %H:%M")]],
                                       columns=["참가자", "기록(초)", "p", "날짜"])
                    old = load_ranking()
                    if len(old) == 0:
                        df = new
                    else:
                        df = pd.concat([old, new])
                    df.to_csv(RANK_FILE, index=False)
                    st.cache_data.clear()
                    rank = len(df[df["기록(초)"] < record]) + 1
                    st.session_state.msg = ("!!! ~~~Congratulation~~~ !!!  " + player + " 기록 "
                                            + str(record) + "초, " + str(rank) + "등")

        st.write(st.session_state.msg)

        @st.fragment()
        def timer():
            st.button("시간 확인")
            if st.session_state.finish:
                st.write("완료 기록:", st.session_state.record, "초")
            else:
                st.write("경과 시간:", int(time.time() - st.session_state.start), "초")

        timer()

    with col1:
        board = pd.DataFrame(st.session_state.board,
                             index=list(range(1, 10)), columns=list(range(1, 10)))
        st.table(board)

with tab2:
    df = load_ranking()
    if len(df) == 0:
        st.write("아직 기록이 없습니다.")
    else:
        st.subheader("전체 순위 TOP 10")
        df = df.sort_values("기록(초)").reset_index(drop=True)
        df.index = df.index + 1
        st.table(df.head(10))

        my = df[df["참가자"] == player].sort_values("날짜").reset_index(drop=True)
        if len(my) > 0:
            st.subheader(player + " 기록 변화")
            my["회차"] = my.index + 1
            st.line_chart(my, x="회차", y="기록(초)")
