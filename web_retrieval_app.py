from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import sys
import streamlit as st
from PIL import Image


def chat(input):
    return chain.invoke({'input': f'{input}'})


def document_from_file(document, p):
    if document.endswith('.md'):
        loader = UnstructuredMarkdownLoader(document)
    else:
        loader = TextLoader(document)

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    vector = FAISS.from_documents(documents, embeddings)

    prompt = ChatPromptTemplate.from_template('''Answer the following question based only on the provided context:

    <context>
    {context}
    </context>

    Question: {input}''')

    document_chain = create_stuff_documents_chain(llm, prompt)

    retriever = vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke(
        {
            'input': p}
        )
    return response['answer']


image = Image.open('images/Asset-Red_Hat-Logo_page-General-This-RGB.png')
st.image(image, output_format='PNG', width=128)
st.title('Red Hat One: Demo - Beyond Automation: Unleashing the Power of AI with Event-Driven Ansible')

temperature_input = st.number_input('Temperature', min_value=0, max_value=9, value=7, step=1, 
                help='Adjusts the creativity and variability of responses from the LLM. Higher values increase creativity at the risk of less predictable outputs. Defaults to a moderate setting for balanced responses.', 
                label_visibility='visible')
t_value = float(f'0.{temperature_input}')

llm_chain = st.radio(
        'Pick a model to use',
        ['llama-pro', 'llama2', 'gpt-3.5-turbo', 'gpt-4'],
        horizontal=True
    )

if llm_chain in ['llama-pro', 'llama2']:
    llm = Ollama(model=llm_chain, temperature=t_value)
    embeddings = OllamaEmbeddings()
elif llm_chain in ['gpt-3.5-turbo', 'gpt-4']:
    llm = ChatOpenAI(model=llm_chain, temperature=t_value)
    embeddings = OpenAIEmbeddings()
else:
    sys.exit('Error: Model not found!')

prompt = ChatPromptTemplate.from_messages([
    ('system', '''
As an expert network architect, your role is pivotal in guiding the engineering team through 
complex design challenges and resolving technical issues with precision. It is imperative 
that you rigorously review your solutions before finalizing them to avoid any potential errors. 
In the event of a misconfiguration, it's crucial to rectify and remove it promptly from the 
device, as leaving such errors unaddressed can lead to significant operational issues. 
Your expertise and attention to detail are key in maintaining the integrity and efficiency of 
the network infrastructure.
     '''),
    ('user', '{input}')
])

output_parser = StrOutputParser()

chain = prompt | llm | output_parser


user_prompt = st.text_area(label='Prompt')

uploaded_file = st.file_uploader('Choose a file')

if user_prompt:
    with st.spinner('Working on it...'):
        if uploaded_file is not None:
            output = document_from_file(uploaded_file.name, user_prompt)
        else:
            output = chat(user_prompt)

        st.write(output)
