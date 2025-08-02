import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from dotenv import load_dotenv
import os

# Load environment variables (for your OpenAI key)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Document classes
class Website:
    def __init__(self, url):
        self.url = url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for tag in soup.body(["script", "style", "img", "input"]):
            tag.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

class PDFFile:
    def __init__(self, file_path):
        self.title = "PDF Document"
        self.text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                self.text += page.get_text()

class TextFile:
    def __init__(self, file_path):
        self.title = "Text File"
        with open(file_path, "r", encoding="utf-8") as f:
            self.text = f.read()

class ImageFile:
    def __init__(self, file_path):
        self.title = "Image Document"
        image = Image.open(file_path)
        self.text = pytesseract.image_to_string(image)

# Prompt structure for OpenAI
def construct_messages(doc):
    return [
        {
            "role": "system",
            "content": "You are an assistant that analyzes the contents of a document or webpage and provides a short summary, ignoring navigation or irrelevant boilerplate text. Respond in markdown."
        },
        {
            "role": "user",
            "content": f"You are analyzing a document titled **{doc.title}**. Please summarize the following content:\n\n{doc.text}"
        }
    ]

# Summarize function
def summarize_document(doc, model="gpt-4"):
    messages = construct_messages(doc)
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )
    return response['choices'][0]['message']['content']

# Streamlit UI
st.title("📄 Document Summarizer with OpenAI")

option = st.radio("Choose input type:", ("Website URL", "Upload PDF", "Upload Text File", "Upload Image"))

doc = None

if option == "Website URL":
    url = st.text_input("Enter a website URL:")
    if url:
        with st.spinner("Fetching and summarizing website..."):
            try:
                doc = Website(url)
                summary = summarize_document(doc)
                st.markdown(summary)
            except Exception as e:
                st.error(f"Error: {e}")

elif option == "Upload PDF":
    uploaded_pdf = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_pdf:
        with st.spinner("Reading and summarizing PDF..."):
            try:
                with open("temp.pdf", "wb") as f:
                    f.write(uploaded_pdf.getbuffer())
                doc = PDFFile("temp.pdf")
                summary = summarize_document(doc)
                st.markdown(summary)
            except Exception as e:
                st.error(f"Error: {e}")

elif option == "Upload Text File":
    uploaded_txt = st.file_uploader("Choose a Text file", type=["txt"])
    if uploaded_txt:
        with st.spinner("Reading and summarizing text file..."):
            try:
                with open("temp.txt", "wb") as f:
                    f.write(uploaded_txt.getbuffer())
                doc = TextFile("temp.txt")
                summary = summarize_document(doc)
                st.markdown(summary)
            except Exception as e:
                st.error(f"Error: {e}")

elif option == "Upload Image":
    uploaded_img = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
    if uploaded_img:
        with st.spinner("Reading and summarizing image text..."):
            try:
                with open("temp_img.png", "wb") as f:
                    f.write(uploaded_img.getbuffer())
                doc = ImageFile("temp_img.png")
                summary = summarize_document(doc)
                st.markdown(summary)
            except Exception as e:
                st.error(f"Error: {e}")
