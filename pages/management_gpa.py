# pages/chat.py

import streamlit as st
from student_manager import StudentManager
from student import Student
from app import get_sign_in_url, generate_sidebar_links
import pandas as pd
import plotly.express as px

# 初始化學生管理器
if 'manager' not in st.session_state:
    st.session_state.manager = StudentManager()


def is_authenticated():
    """
    檢查用戶是否已經認證。
    """
    return 'user' in st.session_state and st.session_state.user is not None


def add_custom_css():
    """
    添加自定義 CSS 來美化應用程式。
    """
    st.markdown("""
        <style>
        /* 全局背景色 */
        .main {
            background-color: #f8f9fa;
        }
        /* 頁面標題樣式 */
        .header {
            text-align: center;
            padding: 10px;
            font-size: 2em;
            color: #343a40;
        }
        /* 表格樣式 */
        .dataframe th, .dataframe td {
            text-align: center;
            padding: 10px;
        }
        /* 按鈕樣式 */
        .stButton>button {
            color: white;
            background-color: #007bff;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        /* 表單標題 */
        .form-title {
            font-size: 1.5em;
            color: #495057;
            margin-bottom: 10px;
        }
        /* 成功訊息 */
        .stSuccess {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        /* 錯誤訊息 */
        .stError {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)


def main():
    add_custom_css()
    st.markdown("<div class='header'>學生管理系統 🎓</div>", unsafe_allow_html=True)

    if not is_authenticated():
        st.warning("請登入以使用學生管理系統。")
        st.stop()

    with st.sidebar:
        # 只有用戶登錄後顯示頁面連結
        if st.session_state.get("user"):
            generate_sidebar_links()
            st.markdown('---')
        else:
            st.write("請登入以訪問應用程式。")
            st.markdown(
                f"[點擊這裡以使用 Azure AD 登入]({get_sign_in_url()})")

    st.markdown("---")

    # 使用頁籤組織不同功能
    tabs = st.tabs(["添加學生", "列出學生", "搜索學生", "插入學生", "移除學生", "數據導入/導出"])

    with tabs[0]:
        # 添加學生模組
        st.subheader("添加新學生")
        with st.form("add_student_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                student_id = st.number_input(
                    "學生 ID", min_value=1, step=1, key="add_id")
            with col2:
                name = st.text_input("姓名", key="add_name")
            with col3:
                gpa = st.number_input("GPA", min_value=0.0,
                                      max_value=4.0, step=0.01, key="add_gpa")
            submitted = st.form_submit_button("添加學生")

            if submitted:
                if name.strip() == "":
                    st.error("姓名不能為空。", icon="🚨")
                else:
                    student = Student(student_id, name, gpa)
                    st.session_state.manager.add_student(student)
                    st.success(f"已添加學生: {student.get_name()}，GPA: {
                               student.get_gpa():.2f}", icon="✅")

    with tabs[1]:
        # 列出學生模組
        st.subheader("列出所有學生")
        list_method = st.radio(
            "選擇列出方法", ["Iterator", "Element Index"], key="list_method", horizontal=True
        )

        if list_method == "Iterator":
            st.write("**List by iterator:**")
            student_list = list(
                st.session_state.manager.list_students_iterator())
        else:
            st.write("**List by element index:**")
            student_list = list(st.session_state.manager.list_students_index())

        if student_list:
            # 使用 DataFrame 顯示學生列表
            data = {
                "ID": [student.ID for student in student_list],
                "姓名": [student.get_name() for student in student_list],
                "GPA": [student.get_gpa() for student in student_list]
            }
            df = pd.DataFrame(data)
            st.dataframe(df.style.set_properties(
                **{'text-align': 'center'}), use_container_width=True)

            # 顯示 GPA 分佈圖表
            fig = px.histogram(df, x='GPA', nbins=20,
                               title='GPA 分佈', labels={'GPA': 'GPA'}, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("目前沒有學生資料。")

    with tabs[2]:
        # 搜索學生模組
        st.subheader("搜索學生")
        search_name = st.text_input("輸入要搜索的學生姓名", key="search_name")
        if st.button("搜索"):
            index = st.session_state.manager.search_student_by_name(
                search_name)
            if index != -1:
                student = st.session_state.manager.students[index]
                st.success(f"找到 {student.get_name()}，其在列表中的位置為: {
                           index + 1}", icon="✅")
                st.write(f"**ID:** {student.ID}")
                st.write(f"**姓名:** {student.get_name()}")
                st.write(f"**GPA:** {student.get_gpa():.2f}")
            else:
                st.error(f"未找到名為 {search_name} 的學生。", icon="🚨")

    with tabs[3]:
        # 插入學生模組
        st.subheader("插入學生")
        with st.form("insert_student_form"):
            insert_index = st.number_input(
                "插入位置 (從 1 開始)", min_value=1, step=1, key="insert_index")
            col1, col2, col3 = st.columns(3)
            with col1:
                insert_id = st.number_input(
                    "學生 ID", min_value=1, step=1, key="insert_id")
            with col2:
                insert_name = st.text_input("姓名", key="insert_name")
            with col3:
                insert_gpa = st.number_input(
                    "GPA", min_value=0.0, max_value=4.0, step=0.01, key="insert_gpa")
            insert_submitted = st.form_submit_button("插入學生")

            if insert_submitted:
                if insert_name.strip() == "":
                    st.error("姓名不能為空。", icon="🚨")
                else:
                    student = Student(insert_id, insert_name, insert_gpa)
                    success = st.session_state.manager.insert_student_at_position(
                        insert_index - 1, student)
                    if success:
                        st.success(f"已在位置 {insert_index} 插入學生: {student.get_name()}，GPA: {
                                   student.get_gpa():.2f}", icon="✅")
                    else:
                        st.error("插入失敗。請檢查插入位置是否有效。", icon="🚨")

    with tabs[4]:
        # 移除學生模組
        st.subheader("移除學生")
        remove_method = st.radio(
            "選擇移除方法", ["移除最後一個學生", "移除特定位置的學生"], key="remove_method", horizontal=True
        )

        if remove_method == "移除最後一個學生":
            if st.button("移除最後一個學生"):
                removed_student = st.session_state.manager.remove_last_student()
                if removed_student:
                    st.success(f"已移除學生: {removed_student.get_name()}，GPA: {
                               removed_student.get_gpa():.2f}", icon="✅")
                else:
                    st.error("沒有學生可以移除。", icon="🚨")
        else:
            with st.form("remove_student_form"):
                remove_index = st.number_input(
                    "輸入要移除的學生位置 (從 1 開始)", min_value=1, step=1, key="remove_index")
                remove_submitted = st.form_submit_button("移除學生")
                if remove_submitted:
                    removed_student = st.session_state.manager.remove_student_at_position(
                        remove_index - 1)
                    if removed_student:
                        st.success(f"已移除學生: {removed_student.get_name()}，GPA: {
                                   removed_student.get_gpa():.2f}", icon="✅")
                    else:
                        st.error("移除失敗。請檢查位置是否有效。", icon="🚨")

    with tabs[5]:
        # 數據導入/導出模組
        st.subheader("數據導入/導出")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 導出學生資料")
            if st.button("下載為 CSV"):
                if st.session_state.manager.students:
                    data = {
                        "ID": [student.ID for student in st.session_state.manager.students],
                        "姓名": [student.get_name() for student in st.session_state.manager.students],
                        "GPA": [student.get_gpa() for student in st.session_state.manager.students]
                    }
                    df = pd.DataFrame(data)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="下載 CSV",
                        data=csv,
                        file_name='students.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("沒有學生資料可以導出。")

        with col2:
            st.markdown("### 導入學生資料")
            uploaded_file = st.file_uploader("上傳 CSV 檔案", type=['csv'])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    if {'ID', '姓名', 'GPA'}.issubset(df.columns):
                        for _, row in df.iterrows():
                            student = Student(
                                int(row['ID']), row['姓名'], float(row['GPA']))
                            st.session_state.manager.add_student(student)
                        st.success("成功導入學生資料。", icon="✅")
                    else:
                        st.error("CSV 檔案必須包含 ID、姓名和 GPA 欄位。", icon="🚨")
                except Exception as e:
                    st.error(f"導入失敗: {e}", icon="🚨")

    st.markdown("---")

    # 確認學生列表
    st.subheader("確認學生列表")
    student_list = list(st.session_state.manager.list_students_index())
    if student_list:
        data = {
            "ID": [student.ID for student in student_list],
            "姓名": [student.get_name() for student in student_list],
            "GPA": [student.get_gpa() for student in student_list]
        }
        df = pd.DataFrame(data)
        st.dataframe(df.style.set_properties(
            **{'text-align': 'center'}), use_container_width=True)
    else:
        st.info("目前沒有學生資料。")


if __name__ == "__main__":
    main()
