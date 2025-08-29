import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

# -------------------------------
# 1. Initialize Groq LLM
# -------------------------------
import os
from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()

os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama3-8b-8192")

# -------------------------------
# 2. Session State for Memory
# -------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        return_messages=True
    )

memory = st.session_state.memory

# -------------------------------
# 3. Create Prompt Template
# -------------------------------
prompt = ChatPromptTemplate.from_template(
    "You are a helpful assistant. Answer the question clearly.\n\n"
    "Chat History:\n{chat_history}\n\n"
    "User Question:\n{question}"
)

# -------------------------------
# 4. Define LLM Chain
# -------------------------------
chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

# -------------------------------
# 5. Streamlit Layout
# -------------------------------
st.set_page_config(page_title="Advanced Groq Chat", layout="wide")
st.title("Context-Aware Conversational AI")
st.markdown("Ask anything! The assistant remembers the conversation context.")

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("Settings & Options")
    if st.button("Clear Conversation"):
        memory.chat_memory.clear()
        st.success("Conversation memory cleared!")

    st.markdown("**Export Conversation:**")
    if st.button("Download Chat as TXT"):
        chat_text = ""
        for msg in memory.chat_memory.messages:
            chat_text += f"{msg.type.upper()} ({datetime.now().strftime('%H:%M')}): {msg.content}\n"
        st.download_button("Download TXT", chat_text, "chat_history.txt")

# -------------------------------
# User Input
# -------------------------------
user_input = st.text_input("Type your question here:")

if st.button("Send") and user_input:
    response = chain.run({"question": user_input})

    # Display response immediately
    st.session_state.latest_response = response

# -------------------------------
# 6. Display Conversation
# -------------------------------
st.subheader("Chat History")
for msg in memory.chat_memory.messages:
    timestamp = datetime.now().strftime("%H:%M")
    if msg.type == "human":
        st.markdown(f"<div style='background-color:#DCF8C6; padding:8px; border-radius:10px;'>**You ({timestamp}):** {msg.content}</div>", unsafe_allow_html=True)
    elif msg.type == "ai":
        st.markdown(f"<div style='background-color:#F1F0F0; padding:8px; border-radius:10px;'>**Assistant ({timestamp}):** {msg.content}</div>", unsafe_allow_html=True)

# Show the latest response separately
if "latest_response" in st.session_state:
    st.markdown(f"<div style='background-color:#F1F0F0; padding:10px; border-radius:10px;'>**Assistant (Latest):** {st.session_state.latest_response}</div>", unsafe_allow_html=True)
