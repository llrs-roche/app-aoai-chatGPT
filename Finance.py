import os
import matplotlib.pyplot as plt
import streamlit as st
from openai import AzureOpenAI
import base64
from PIL import Image

# Configuraciones - API de Azure OpenAI
endpoint = os.getenv("ENDPOINT_URL", "https://cog-aoai-team-es6-ac4f.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")  
search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://srch-team-es6-ac4f.search.windows.net")  
search_key = os.getenv("SEARCH_KEY", "NULL")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "NULL")

# Inicializar el cliente de Azure OpenAI con autenticación basada en clave
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)


#### Config Page Streamlit
imagen = Image.open('./images/blue_logo.png')

def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style> 
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

st.set_page_config(page_title="Finance Roche ChatBot", page_icon=imagen,layout="centered")

st.logo(
    image="./images/white_logo.png"        #/app/Design/blue_logo.png
)

set_bg_hack("./images/Finance_Background.png")

##################################################################
# Generación de resumen de salida
def output_generation_summary(input_text, search_endpoint, search_key):    
    if not search_endpoint or not search_key:
        return "Error: search_endpoint o search_key no están configurados correctamente."
 
    try:
        # Generar la respuesta
        completion = client.chat.completions.create(
            model=deployment,
            messages=input_text,
            max_tokens=800,
            temperature=0.7, # 0.0 
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False,
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": search_endpoint,
                            "index_name": "finance-group6-index-v2",
                            "semantic_configuration": "default",
                            "query_type": "semantic",
                            "fields_mapping": {},
                            "in_scope": True,
                            "role_information": (
                                "You are a finance expert assisting with data inquiries. If clarification is needed, "
                                "prompt the user directly."
                            ),
                            "filter": None,
                            "strictness": 3,
                            "top_n_documents": 10,
                            "authentication": {
                                "type": "api_key",
                                "key": search_key,
                            },
                        },
                    }
                ]
            },
        )
        if completion and completion.choices:
            content = completion.choices[0].message.content
            return content
        else:
            return "Error: No se pudo generar la respuesta."
    
    except Exception as e:
        return f"Error al generar la respuesta: {e}"

def test (input_text, search_endpoint, search_key):
    return input_text   
   
messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant, expert in finance and help people find information about Roche.\n"
                "Your responses must be concise and limited to one line wherever possible. Provide only the exact "
                "answer to the user’s question without additional explanations. If the input lacks detail, prompt "
                "for more specifics, e.g., \"Could you provide more details on…?\".\n"
                "Answer in the user's language and avoid topics outside Roche's financial data."
            ),
        },        
    ]

st.title("Finance Roche ChatBot")
st.write("Welcome to this Chatbot to manage Roche financial data.")

# Inicializar el historial de preguntas y respuestas
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Mostrar el cuadro de texto con marcador de posición
            #user_input = st.text_area("Type your financial question here:", placeholder="None")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#user input
if prompt := st.chat_input("Please enter a query to get started"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content":prompt})
    messages.append({"role": "user","content":prompt})
 
    #st.write(messages)

    response = output_generation_summary(messages, search_endpoint, search_key)
    #st.write(messages)

    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role":"assistant","content":response})