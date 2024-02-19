import streamlit as st
from src.utils import (
    prepare_data_for_mistral,
    get_answer
    )


st.title("RAG application on PDF question answering")

documents, nodes, collection = prepare_data_for_mistral(
    use_dir=True
    )


section_key = "RAG_PDFs_data"
if f"messages_{section_key}" not in st.session_state:
    st.session_state[f"messages_{section_key}"] = []

question_input = st.chat_input(
    "Ask a question:",
    key=f"question_input_{section_key}"
    )

if question_input:
    try:
        if collection is not None:
            chat_response = get_answer(
                question_input,
                collection,
                prompt_key="RAG_PDFs_data"
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
