# Antes de ejecutar:  pip install "azure-ai-projects>=2.1.0" azure-identity openai
# Ejecutar con:       python windcare_terminal.py

from azure.identity import DefaultAzureCredential   # Autenticación con tu sesión de "az login" (sin API keys)
from azure.ai.projects import AIProjectClient       # Cliente del SDK de Microsoft Foundry

ENDPOINT = "https://foundry-tecnun-resource.services.ai.azure.com/api/projects/foundry-tecnun-project"  # Proyecto de Foundry
AGENT_NAME = "agent-alex-wind"                      # Agente de mantenimiento creado en el portal


def gestionar_aprobaciones(openai_client, conversation_id, response):
    """Si el agente pide permiso para usar una herramienta MCP (GitHub), pregunta al usuario y responde."""
    while True:                                                                  # Puede haber varias peticiones seguidas
        peticiones = [o for o in response.output                                 # Busca en la respuesta los elementos
                      if getattr(o, "type", "") == "mcp_approval_request"]       # que son peticiones de aprobación MCP
        if not peticiones:                                                       # Si no hay ninguna, la respuesta ya es final
            return response
        respuestas = []                                                          # Aquí guardamos las decisiones del usuario
        for p in peticiones:                                                     # Para cada petición
            print(f"\n[MCP] El agente quiere usar '{p.name}' en el servidor '{p.server_label}'")  # Qué herramienta quiere usar
            print(f"      Argumentos: {p.arguments}")                            # Con qué datos (repo, issue...)
            decision = input("      ¿Aprobar? (s/n): ").strip().lower()          # Pregunta al usuario
            respuestas.append({                                                  # Prepara la respuesta de aprobación
                "type": "mcp_approval_response",
                "approval_request_id": p.id,                                     # A qué petición respondemos
                "approve": decision.startswith("s"),                             # True si ha escrito "s"
            })
        response = openai_client.responses.create(                               # Envía las decisiones al agente
            conversation=conversation_id,                                        # En la misma conversación
            input=respuestas,
        )                                                                        # Y vuelve a comprobar si pide más


def main():
    with (
        DefaultAzureCredential() as credential,     # Obtiene tus credenciales de Azure
        AIProjectClient(                            # Conecta con el proyecto de Foundry
            endpoint=ENDPOINT,
            credential=credential,
            allow_preview=True,                     # Necesario para los agentes nuevos (preview)
        ) as project_client,
    ):
        openai_client = project_client.get_openai_client(agent_name=AGENT_NAME)  # Cliente "atado" a agent-alex-wind
        conversation = openai_client.conversations.create()                     # Conversación con memoria entre preguntas

        print("=" * 60)                                                         # Línea decorativa
        print(" WindCare - Mendibeltz Wind Farm maintenance assistant")         # Título del programa
        print(" Escribe tu pregunta ('salir' para terminar)")                   # Instrucciones de uso
        print("=" * 60)

        while True:                                                             # Bucle de chat
            pregunta = input("\nTú: ").strip()                                  # Lee la pregunta y quita espacios
            if not pregunta:                                                    # Si está vacía, vuelve a preguntar
                continue
            if pregunta.lower() == "salir":                                     # Con "salir" termina
                print("Hasta luego.")
                break
            try:
                response = openai_client.responses.create(                      # Envía la pregunta al agente
                    conversation=conversation.id,                               # Dentro de la misma conversación
                    input=[{"role": "user", "content": pregunta}],              # Mensaje del usuario
                )
                response = gestionar_aprobaciones(openai_client, conversation.id, response)  # Gestiona permisos de GitHub
                print(f"\nWindCare: {response.output_text}")                    # Muestra la respuesta final
                if not response.output_text:                                    # Si sigue vacía, muestra qué devolvió el agente
                    print("[Debug] Tipos recibidos:", [getattr(o, "type", "?") for o in response.output])
            except Exception as e:                                              # Si algo falla, no se cierra el programa
                print(f"\n[Error al llamar al agente] {e}")                     # Muestra el error y sigue


if __name__ == "__main__":                                                      # Punto de entrada del script
    main()