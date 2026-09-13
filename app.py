
import streamlit as st

# page setup
st.set_page_config(
    page_title="StudentOS",
    page_icon="🎓"
)

# title
st.title("🎓 StudentOS 🎓")

st.write("Organize your assignments and stay on track.")



#this is 4 manual input

st.subheader("Add an Assignment")

assignment_name = st.text_input("Assignment Name")

subject = st.text_input("Class / Subject")

due_date = st.date_input("Due Date")

description = st.text_area("Description (Optional)")


if st.button("Add Assignment"):

    if assignment_name and subject:

        st.success("Assignment Added!")

        st.write("### Assignment Information")

        st.write("Assignment:", assignment_name)
        st.write("Class:", subject)
        st.write("Due Date:", due_date)

    else:

        st.warning("Please enter an assignment name and subject.")
