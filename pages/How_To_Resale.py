import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain_openai import OpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
import requests
from bs4 import BeautifulSoup
import logging
from helper_functions.utility import check_password

# --------------------------
# 1. Configure Logging
# --------------------------
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# --------------------------
# 2. Load Environment Variables
# --------------------------
openai_api_key = st.secrets["openai"]["openai_api_key"]

if not openai_api_key:
    st.error("OpenAI API key not found. Please ensure it is properly set in the secrets.toml file.")
    st.stop()

# --------------------------
# 3. Initialize OpenAI Components
# --------------------------
try:
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
except Exception as e:
    logging.error(f"Error initializing OpenAI components: {e}")
    st.error("Failed to initialize OpenAI components. Check the logs for details.")
    st.stop()

# --------------------------
# 4. Fetch and Process Data from HDB Website
# --------------------------
@st.cache_data(ttl=3600)  # Cache the data for 1 hour to improve performance
def fetch_hdb_resale_data():
    hdb_urls = [
        "https://www.mymoneysense.gov.sg/buying-a-house/purchase-guide/new-or-resale-flat",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/overview",
        "https://www.hdb.gov.sg/residential/buying-a-flat/understanding-your-eligibility-and-housing-loan-options/application-for-an-hdb-flat-eligibility-hfe-letter",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/planning-considerations",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/mode-of-financing",
        "https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/understanding-your-eligibility-and-housing-loan-options/flat-and-grant-eligibility/couples-and-families/cpf-housing-grants-for-resale-flats-families",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/option-to-purchase",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/request-for-value",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/resale-application/application",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/resale-application/acceptance-and-approval",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/resale-completion",
        "https://www.hdb.gov.sg/residential/buying-a-flat/conditions-after-buying"
    ]
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/116.0.0.0 Safari/537.36"
        )
    }

    hdb_resale_text = ""
    for url in hdb_urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an error for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            hdb_resale_text += "\n".join([para.get_text() for para in paragraphs]) + "\n"

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from {url}: {e}")
            st.error(f"Failed to fetch HDB resale data from {url}. Check logs for more details.")
            return ""

    if not hdb_resale_text.strip():
        logging.error("No textual content found on the specified HDB resale pages.")
        st.error("No textual content found. Please check the logs.")
        return ""

    return hdb_resale_text

hdb_resale_text = fetch_hdb_resale_data()

# --------------------------
# 5. Split Text into Chunks
# --------------------------
try:
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separator="\n"
    )
    documents = text_splitter.split_text(hdb_resale_text)
except Exception as e:
    logging.error(f"Error splitting text: {e}")
    st.error("Failed to process the fetched data.")
    st.stop()

# --------------------------
# 6. Create Embeddings and Vector Store
# --------------------------
try:
    vectorstore = FAISS.from_texts(
        [doc for doc in documents],
        embeddings
    )
except Exception as e:
    logging.error(f"Error creating vector store: {e}")
    st.error("Failed to create vector store. Check the logs for details.")

# --------------------------
# 7. Set Up Retrieval QA Chain
# --------------------------
template = """Use the following pieces of context to answer the question at the end. 
If the answer cannot be found, respond that you are unable to assist with the query. 
Use three sentences maximum. Keep the answer as concise as possible. Use bolding to emphasize key words and phrases. 
Adopt a soothing and pleasant tone in the response, especially if the query cannot be answered.
Always say "Feel Free to let us know if you have any other questions!" at the end of the answer.

{context}
Question: {question}
Helpful Answer:"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

try:
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,  # Set to False to hide source documents
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
except Exception as e:
    logging.error(f"Error setting up Retrieval QA chain: {e}")
    st.error("Failed to set up QA chain. Check the logs for details.")

# --------------------------
# 8. Streamlit Chatbot Interface
# --------------------------
if not check_password():
    st.stop()

# Create two columns: one for the title and one for the image
col1, col2 = st.columns([3, 1])  # Adjust the ratios as needed

with col1:
    st.title("How to Resale")

st.write("Unsure about HDB resale and processes? Fred not, let us help u out!")

user_question = st.text_input("Your Question:")

if st.button("Get Answer"):
    if user_question.strip():
        with st.spinner("Fetching answer..."):
            try:
                result = qa_chain({"query": user_question})
                answer = result.get('result', "I'm sorry, I couldn't retrieve an answer.")
                st.write(answer)
            except Exception as e:
                logging.error(f"Error during QA chain execution: {e}")
                st.error("An error occurred while fetching the answer. Please try again later.")
    else:
        st.warning("Please enter a question.")
