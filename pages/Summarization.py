import streamlit as st
from src.utils import (
    upload_pdf,
    display_pdf,
    prepare_data_for_mistral,
    get_summary)


st.set_page_config(layout="wide")
st.title("PDF summary")

col1, col2 = st.columns(2)

with col2:
    uploaded_file = upload_pdf()

if uploaded_file is not None:
    with col1:
        documents, nodes, collection = prepare_data_for_mistral(
            uploaded_file=uploaded_file,
            include_collection=False
            )
        resume = get_summary(documents)
        st.markdown(resume)
    with col2:
        display_pdf(uploaded_file)
