import streamlit as st
from src.utils import (
    upload_pdf,
    display_pdf,
    prepare_data_for_mistral,
    initialize_LLM_model,
    get_answer
    )


st.set_page_config(layout="wide")
st.title("PDF question answering")

col1, col2 = st.columns(2)

with col2:
    uploaded_file = upload_pdf()

if uploaded_file is not None:
    initialize_LLM_model()
    with col1:
        documents, nodes, collection = prepare_data_for_mistral(
            uploaded_file=uploaded_file
            )

        section_key = "RAG_PDF"
        if f"messages_{section_key}" not in st.session_state:
            st.session_state[f"messages_{section_key}"] = []

        question_input = st.text_input(
            "Ask a question:",
            key=f"question_input_{section_key}"
            )

        if st.button("Ask"):
            try:
                if collection is not None:
                    chat_response = get_answer(
                        question_input,
                        collection,
                        prompt_key="RAG_PDF"
                        )
                    st.session_state[f"messages_{section_key}"].append(
                        {
                            "role": "user",
                            "content": question_input
                            }
                            )
                    st.session_state[f"messages_{section_key}"].append(
                        {
                            "role": "assistant",
                            "content": chat_response
                            }
                            )
            except Exception as e:
                st.session_state[f"messages_{section_key}"].append(
                    {
                        "role": "assistant",
                        "content": f"Error: {str(e)}"
                        }
                        )
                st.error("Failed to process the question.")

        for message in st.session_state[f"messages_{section_key}"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    with col2:
        display_pdf(uploaded_file)
