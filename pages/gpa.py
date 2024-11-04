# pages/chat.py

import streamlit as st
from llm_service import LLMService
from app import get_sign_in_url, generate_sidebar_links

GRADE_POINT_MAPPING = {
    'A+': 4.3,
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.3,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.3,
    'C': 2.0,
    'C-': 1.7,
    'D+': 1.3,
    'D': 1.0,
    'F': 0.0
}


def calculate_gpa(grades, credits, grade_point_mapping=GRADE_POINT_MAPPING):
    """
    計算 GPA 的函數。

    參數：
    - grades: List[str]，每門課程的成績（例如 ['A', 'B+', 'C']）
    - credits: List[float]，每門課程的學分（例如 [3, 4, 2]）
    - grade_point_mapping: Dict[str, float]，成績到點數的映射

    返回：
    - float，計算出的 GPA，保留兩位小數

    範例：
    >>> grades = ['A', 'B+', 'C', 'A-', 'B']
    >>> credits = [3, 4, 2, 3, 3]
    >>> calculate_gpa(grades, credits)
    3.26
    """
    if len(grades) != len(credits):
        raise ValueError("成績列表和學分列表的長度必須相同。")

    total_points = 0.0
    total_credits = 0.0

    for grade, credit in zip(grades, credits):
        grade = grade.upper()
        if grade not in grade_point_mapping:
            raise ValueError(f"無效的成績: {grade}")
        grade_point = grade_point_mapping[grade]
        total_points += grade_point * credit
        total_credits += credit

    if total_credits == 0:
        return 0.0

    gpa = total_points / total_credits
    return round(gpa, 2)


def is_authenticated():
    """
    檢查用戶是否已經認證。
    """
    return 'user' in st.session_state and st.session_state.user is not None


def main():
    st.title("GPA Calculator 🎓")

    if not is_authenticated():
        st.warning("Please log in to use the assistant.")
        st.stop()

    with st.sidebar:
        # 只有用戶登錄後顯示頁面連結
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("Please log in to access the application.")
            st.markdown(
                f"[Click here to log in with Azure AD]({get_sign_in_url()})")

    st.header("計算您的 GPA")

    st.write("請輸入您的課程成績和對應的學分，然後點擊 **計算 GPA** 按鈕。")

    # 使用 Session State 來儲存課程數據
    if 'courses' not in st.session_state:
        st.session_state.courses = [{'grade': '', 'credit': ''}]

    def add_course():
        st.session_state.courses.append({'grade': '', 'credit': ''})

    def remove_course(index):
        st.session_state.courses.pop(index)

    # 顯示每門課程的輸入欄位
    for idx, course in enumerate(st.session_state.courses):
        cols = st.columns([2, 1, 1])
        with cols[0]:
            course['grade'] = st.text_input(
                f"課程 {idx + 1} 成績", value=course['grade'], key=f"grade_{idx}")
        with cols[1]:
            course['credit'] = st.text_input(
                f"課程 {idx + 1} 學分", value=course['credit'], key=f"credit_{idx}")
        with cols[2]:
            if st.button("移除", key=f"remove_{idx}"):
                remove_course(idx)
                st.rerun()

    st.button("新增課程", on_click=add_course)

    # 按鈕計算 GPA
    if st.button("計算 GPA"):
        grades = []
        credits = []
        error = False

        for course in st.session_state.courses:
            grade = course['grade'].strip().upper()
            credit = course['credit'].strip()

            if not grade or not credit:
                st.error("所有課程的成績和學分都必須填寫。")
                error = True
                break

            try:
                credit = float(credit)
                if credit <= 0:
                    st.error("學分必須為正數。")
                    error = True
                    break
            except ValueError:
                st.error(f"無效的學分值: {credit}")
                error = True
                break

            grades.append(grade)
            credits.append(credit)

        if not error:
            try:
                gpa = calculate_gpa(grades, credits)
                st.success(f"您的 GPA 是: **{gpa}**")
            except ValueError as ve:
                st.error(f"計算 GPA 時出錯: {ve}")

    # 可選：提供清除所有輸入的按鈕
    if st.button("清除所有輸入"):
        st.session_state.courses = [{'grade': '', 'credit': ''}]
        st.rerun()


if __name__ == "__main__":
    main()
