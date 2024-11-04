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
@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def fetch_hdb_resale_data():
    hdb_urls = [
        "https://www.mymoneysense.gov.sg/buying-a-house/purchase-guide/new-or-resale-flat",
        "https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats",
        # Additional URLs...
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
            response.raise_for_status()
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
Always say "Feel free to let us know if you have any other questions!" at the end of the answer.

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
        return_source_documents=False,
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

# Add custom styling for a better user experience
st.markdown("""
    <style>
        .stApp {
            background-color: #f7f9fc;
            font-family: 'Arial', sans-serif;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .description {
            text-align: center;
            font-size: 18px;
            color: #34495e;
        }
        .stButton>button {
            background-color: #2980b9;
            color: white;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #1f6391;
        }
        .stTextInput {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Create two columns: one for the title and one for the image (if needed)
col1, col2 = st.columns([3, 1])  # Adjust the ratios as needed

with col1:
    st.title("🏠 HDB Resale Guide")
    st.write("Unsure about HDB resale and processes? Fear not, let us help you out!")

with col2:
    # You can add an image or additional content in the second column if desired
    st.image("your_image_path.png", width=100)  # Replace with an actual image path

# User input for questions
user_question = st.text_input("Your Question:", placeholder="Type your question here...")

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
