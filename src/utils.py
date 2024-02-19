import chromadb
from chromadb.api.models.Collection import Collection
import streamlit as st
from llama_index.node_parser import SimpleNodeParser
from llama_index.schema import Document, BaseNode
from llama_index import SimpleDirectoryReader
from pypdf import PdfReader
from typing import List, Tuple, Optional, Match
from io import BytesIO
import base64
from mistralai.models.chat_completion import ChatMessage
from src.prompts import PROMPTS
import re
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


tokenizer: Optional[AutoTokenizer] = None
model: Optional[AutoModelForCausalLM] = None


def initialize_LLM_model(
        model_name: str = "mistralai/Mistral-7B-v0.1"):
    """
    IInitializes and loads the tokenizer and the model into memory.

    Args:
        model_name (str): The name of the model on Hugging Face.
    """
    global tokenizer, model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, load_in_4bit=True)

    if torch.cuda.is_available():
        model.to("cuda")


def prepare_data_for_mistral(
        uploaded_file: Optional[BytesIO] = None,
        use_dir: bool = False,
        include_collection: bool = True
        ) -> Tuple[
            List[Document],
            Optional[List[BaseNode]],
            Optional[Collection]
            ]:
    """
    This unified method aims to prepare data to send it to the Mistral LLM
    """
    if use_dir:
        documents = load_dir()
    else:
        if uploaded_file is not None:
            documents = load_PDF(uploaded_file)

    collection = None
    nodes = None
    if include_collection:
        nodes = parse_PDF(documents)
        collection = vectorDB(nodes)

    return documents, nodes, collection


def upload_pdf() -> Optional[BytesIO]:
    uploaded_file = st.file_uploader("Download PDF", type="pdf")
    if uploaded_file is not None:
        return uploaded_file
    else:
        return None


def display_pdf(uploaded_file: BytesIO) -> None:
    """Display uploaded PDF in streamlit."""
    # Read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # Convert to utf-8
    base64_pdf = base64.b64encode(bytes_data).decode("utf-8")
    # Embed PDF in HTML
    width = 800
    pdf_display = f'<iframe src=' \
        f'"data:application/pdf;base64,{base64_pdf}#toolbar=0"' \
        f'width={str(width)} height={str(width*4/3)}' \
        'type="application/pdf"></iframe>'
    # Display file
    st.markdown(pdf_display, unsafe_allow_html=True)


@st.cache_resource()
def load_PDF(uploaded_file: BytesIO) -> List:
    """Load uploaded PDF file into one document."""
    pdf = PdfReader(uploaded_file)
    documents = []
    text = ""
    filename = f"{uploaded_file.name}"
    for page in range(len(pdf.pages)):
        text += pdf.pages[page].extract_text()
        documents.append(
            Document(
                text=text,
                extra_info={'page_label': page, 'file_name': filename}))
    return documents


@st.cache_resource()
def load_dir() -> List:
    """Load PDF files in the data directory."""
    try:
        documents = SimpleDirectoryReader(input_dir="./data").load_data()
        if not documents:
            raise ValueError("No documents found in './data'")
        return documents
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        raise


def parse_PDF(documents: List) -> List[BaseNode]:
    """Parse PDF into nodes."""
    node_parser = SimpleNodeParser.from_defaults(chunk_size=5000)
    nodes = node_parser.get_nodes_from_documents(documents)
    return nodes


def vectorDB(nodes: List[BaseNode]) -> Collection:
    """Create and embed pdf in a vector database."""
    try:
        chroma_client = chromadb.Client()
        collection = chroma_client.get_or_create_collection(
            name="test",
            metadata={"hnsw:space": "cosine"})
        for i, node in enumerate(nodes):
            collection.add(
                documents=[node.get_content()],
                metadatas=[
                    {'source': f'{node.get_metadata_str()}'}
                    ],
                ids=[f'{i}'])
        return collection
    except Exception as e:
        st.error(f"Error setting up the vector database: {str(e)}")
        raise


def get_summary(
        docs: List
        ) -> str:
    """Receive the PDF uploaded and make a summary"""
    messages = [
        ChatMessage(
            role="user",
            content=f"Make a summary written in the third person plural 'they'"
            f"of the following scientific paper PDF:"
            f"{docs[0].text} and write it in the following form: the title,"
            f"the authors, an abstract, the main contributionn,"
            f"the key findings, and a conclusion."
            )
            ]
    try:
        assert tokenizer is not None and model is not None

        inputs = tokenizer(messages, return_tensors="pt").to(0)
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")

        outputs = model.generate(**inputs)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer

    except Exception as e:
        st.error(f"Failed to get answer: {str(e)}")
        raise


def get_answer(
        question_input: str,
        collection: Collection,
        prompt_key: str) -> str:
    """
    Question answering function based on Retrieved information (chunk of PDF)
    """
    try:
        dbresults = collection.query(query_texts=[question_input])
        if dbresults is not None:
            documents = dbresults.get('documents')
            metadatas = dbresults.get('metadatas')
            if documents and metadatas is not None:
                content = documents[0][0]
                source = metadatas[0][0]['source']
            page_number_match: Optional[Match[str]] = re.search(
                r"page_label: (\d+)", str(source)
                )
            filename_match: Optional[Match[str]] = re.search(
                r"file_name: (.+)", str(source)
                )

            page_number = (page_number_match.group(1) if page_number_match
                           else "Unknown")
            filename = (filename_match.group(1) if filename_match
                        else "Unknown")

            prompt_template = PROMPTS[prompt_key]
            prompt = prompt_template.format(
                question=question_input,
                content=content,
                filename=filename,
                page_number=page_number
                )

            assert tokenizer is not None and model is not None

            inputs = tokenizer(prompt, return_tensors="pt").to(0)
            if torch.cuda.is_available():
                inputs = inputs.to("cuda")

            outputs = model.generate(**inputs)
            answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

        else:
            answer = ""
        return answer
    except Exception as e:
        st.error(f"Failed to get answer: {str(e)}")
        raise
