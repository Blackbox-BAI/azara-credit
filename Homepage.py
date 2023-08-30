import streamlit as st
from azara_utils import parse_docx, parse_pdf, parse_txt, count_tokens_return_length_price, calculate_azara_credit
from scenarios import ScenarioClass
from integrations import IntegrationCosts
import pandas as pd

st.set_page_config(layout="wide")
st.title("Azara Credit Calculator v1.0")

# Import classes
scenarioClass = ScenarioClass()
integration_costs = IntegrationCosts()

# Create a dropdown menu in the sidebar to select pages
st.sidebar.markdown("## Menu")
st.sidebar.markdown("Select a scenario to run the calculation")
st.sidebar.markdown("1. User uploads a file for embedding")
st.sidebar.markdown("2. User chats with an agent for data retrieval")

scenario = st.sidebar.selectbox(
    "Navigation", ("Credit Calculation", "Scenario 1", "Scenario 2"))

# Main content based on scenario selection
if scenario == "Scenario 1":
    scenarioClass.scenario_one()

elif scenario == "Scenario 2":
    scenarioClass.scenario_two()

else:

    col1, col2 = st.columns(2)
    AZARA_MARGIN = col1.slider(
        "Azara Margin (%)", min_value=0.0, max_value=100.0, value=80.0, step=1.0)
    AWS_COST = col2.slider("AWS Cost ($/hour)", min_value=0.0,
                           max_value=100.0, value=0.1, step=0.1)

    # Inputs for GPT Token
    col1, col2, col3 = st.columns((3, 1, 2))
    with col1:
        st.header("LLM")
        model = st.radio("Which model will you use?",
                         ("gpt-4-8k", "gpt-4-32k", "gpt-3.5-turbo"))
        st.session_state["MODEL"] = model

        # Enter text for LLM
        text = st.text_area("Enter text for LLM", height=100)
        cal_button = st.button("Token Costs")

        if cal_button and text:

            length, price = count_tokens_return_length_price(
                text, st.session_state["MODEL"])
            st.markdown(f'GPT model: **{st.session_state["MODEL"]}**')
            st.markdown(f"Estimated Words: **{len(text.split())}**")
            st.markdown(f"Estimated Tokens: **{length}**")
            st.markdown(f"Estimated Price (USD): **${price:g}**")

        number_of_words = len(text.split()) if text else 0

    # Inputs for Pinecone
    with col2:
        st.header("Pinecone")
        pinecode_pods = st.number_input(
            "Number of Pods", min_value=1, max_value=5, value=1)
        pinecone_retrievel_duration = st.number_input(
            "Document Retrieval Duration (seconds)", min_value=0, max_value=1000, value=30, step=1)
        pinecone_cost_per_hour = 0.096
        cloud_provider = st.selectbox(
            "Cloud Provider", ("aws", "gcp", "azure"))
        storage_type = 's1'
        instance_type = st.selectbox("Instance Type", ("x1", "x2", "x4", "x8"))

    # Inputs for document upload
    with col3:
        st.header("Document")
        uploaded_file = st.file_uploader(
            "Upload a txt file", type=["pdf", "docx", "txt"])
        if uploaded_file:
            doc = None

            if uploaded_file.name.endswith(".txt"):
                doc = parse_txt(uploaded_file)

            elif uploaded_file.name.endswith(".docx"):
                doc = parse_docx(uploaded_file)

            elif uploaded_file.name.endswith(".pdf"):
                doc = parse_pdf(uploaded_file)

            else:
                raise ValueError("File type not supported!")

            length, price = count_tokens_return_length_price(
                doc, st.session_state["MODEL"])
            doc_button = st.button("Document Cost")

            if doc_button:
                st.markdown(f'GPT model: {st.session_state["MODEL"]}')
                st.markdown(f"Estimated Words: {len(doc)}")
                st.markdown(f"Estimated Tokens: {length}")
                st.markdown(f"Estimated Price (USD): ${price:g}")

            number_of_words = len(text.split()) if text else len(doc)

    if st.button("Estimated Azara Credit for Document Embedding"):

        credit = calculate_azara_credit(number_of_words, pinecode_pods, pinecone_retrievel_duration,
                                        st.session_state["MODEL"], cloud_provider, storage_type, instance_type)
        df = pd.DataFrame(
            {
                "Azara Credit ($)": [credit],
                "Azara Credit with Margin ($)": [credit * (1 + AZARA_MARGIN / 100)],
                "Azara Credit with AWS Cost ($)": [credit + AWS_COST],
                "Azara Credit with Margin and AWS Cost ($)": [credit * (1 + AZARA_MARGIN / 100) + AWS_COST],
            }
        )
        st.table(df)
