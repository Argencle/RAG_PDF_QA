import streamlit as st
from src.utils import initialize_LLM_model


def main():
    st.title(
        "This is a replica of the AskYourPDF Application"
        )
    initialize_LLM_model()


if __name__ == "__main__":
    main()
