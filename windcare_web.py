# Antes de ejecutar:  pip install streamlit "azure-ai-projects>=2.1.0" azure-identity openai
# Ejecutar con:       streamlit run windcare_web.py

import streamlit as st                              # Librería para crear la web en Python
from azure.identity import DefaultAzureCredential   # Autenticación con "az login"
from azure.ai.projects import AIProjectClient       # SDK de Microsoft Foundry

ENDPOINT = "https://foundry-tecnun-resource.services.ai.azure.com/api/projects/foundry-tecnun-project"  # Proyecto
AGENT_NAME = "agent-alex-wind"                      # Agente de mantenimiento

st.set_page_config(page_title="WindCare", page_icon="🌬️")   # Título e icono de la pestaña del navegador
st.title("🌬️ WindCare")                                      # Título grande de la página
st.caption("Maintenance assistant · Mendibeltz Wind Farm · Haizea Renewables")  # Subtítulo

@st.cache_resource                                  # Crea la conexión una sola vez (no en cada mensaje)
def get_client():
    project_client = AIProjectClient(               # Conecta con el proyecto de Foundry
        endpoint=ENDPOINT,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )
    return project_client.get_openai_client(agent_name=AGENT_NAME)  # Cliente atado al agente

client = get_client()                               # Obtiene el cliente (reutilizado entre mensajes)

if "conversation_id" not in st.session_state:       # Primera vez que se abre la página
    st.session_state.conversation_id = client.conversations.create().id  # Crea una conversación nueva
    st.session_state.messages = []                  # Lista para guardar el historial que se muestra

with st.sidebar:                                    # Barra lateral izquierda
    st.header("Ejemplos")                           # Título de la barra lateral
    st.markdown("- What does alarm code E-110 mean?\n"
                "- Max wind speed to enter the hub?\n"
                "- Is WTG-03 affected by any service bulletin?")  # Preguntas de ejemplo
    if st.button("Nueva conversación"):             # Botón para empezar de cero
        st.session_state.conversation_id = client.conversations.create().id  # Nueva conversación
        st.session_state.messages = []              # Borra el historial mostrado
        st.rerun()                                  # Recarga la página

for msg in st.session_state.messages:               # Pinta los mensajes anteriores
    with st.chat_message(msg["role"]):              # Burbuja de usuario o de asistente
        st.markdown(msg["content"])                 # Texto del mensaje

pregunta = st.chat_input("Escribe tu pregunta sobre los aerogeneradores...")  # Caja de texto inferior
if pregunta:                                        # Si el usuario ha escrito algo
    st.session_state.messages.append({"role": "user", "content": pregunta})  # Guarda la pregunta
    with st.chat_message("user"):                   # Muestra la pregunta en pantalla
        st.markdown(pregunta)
    with st.chat_message("assistant"):              # Burbuja de respuesta
        with st.spinner("WindCare está pensando..."):  # Animación de "cargando"
            try:
                response = client.responses.create(  # Envía la pregunta al agente
                    conversation=st.session_state.conversation_id,
                    input=[{"role": "user", "content": pregunta}],
                )
                respuesta = response.output_text    # Texto de la respuesta
            except Exception as e:                  # Si algo falla
                respuesta = f"⚠️ Error al llamar al agente: {e}"  # Mensaje de error
        st.markdown(respuesta)                      # Muestra la respuesta
    st.session_state.messages.append({"role": "assistant", "content": respuesta})  # Guarda la respuesta