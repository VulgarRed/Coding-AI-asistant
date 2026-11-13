"""Asistente Virtual de la Clase.

Aplicación de chat en Streamlit que consulta el modelo openai/gpt-oss-20b
a través de la API de Groq y conserva el historial durante la sesión.
"""

import streamlit as st
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)

# ----------------------------------------------------------------------------
# Configuración general
# ----------------------------------------------------------------------------
MODELO = "openai/gpt-oss-20b"
NOMBRE_SECRETO = "LLAVE_PROFESOR"
MAX_MENSAJES_CONTEXTO = 20  # Últimos mensajes que se envían al modelo.

PROMPT_SISTEMA = (
    "Eres el Asistente Virtual de la Clase, un tutor académico amable, claro "
    "y paciente. Responde siempre en español, de forma precisa y bien "
    "estructurada, usando ejemplos cuando ayuden a comprender. Si no sabes "
    "algo o la pregunta es ambigua, dilo con honestidad y pide aclaraciones."
)

st.set_page_config(
    page_title="Asistente Virtual de la Clase",
    page_icon="🎓",
    layout="centered",
)


# ----------------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------------
def obtener_cliente() -> Groq | None:
    """Crea el cliente de Groq leyendo la clave desde st.secrets.

    Devuelve None y muestra un mensaje de error si la configuración
    es incorrecta.
    """
    try:
        clave = st.secrets[NOMBRE_SECRETO]
    except FileNotFoundError:
        st.error(
            "⚠️ No se encontró el archivo de secretos. Crea "
            "`.streamlit/secrets.toml` (ejecución local) o configura los "
            "*Secrets* en Streamlit Community Cloud."
        )
        return None
    except KeyError:
        st.error(
            f"⚠️ Falta la clave `{NOMBRE_SECRETO}` en la configuración de "
            "secretos. Agrégala en `secrets.toml` o en los *Secrets* de "
            "Streamlit Community Cloud."
        )
        return None
    except Exception as error:  # noqa: BLE001
        st.error(f"⚠️ No se pudieron leer los secretos: {error}")
        return None

    if not isinstance(clave, str) or not clave.strip():
        st.error(
            f"⚠️ La clave `{NOMBRE_SECRETO}` está vacía. Escribe una clave "
            "de API válida de Groq."
        )
        return None

    return Groq(api_key=clave.strip())


def generar_respuesta(cliente: Groq, historial: list[dict]):
    """Genera fragmentos de texto de la respuesta del modelo (streaming)."""
    mensajes = [{"role": "system", "content": PROMPT_SISTEMA}]
    mensajes += historial[-MAX_MENSAJES_CONTEXTO:]

    flujo = cliente.chat.completions.create(
        model=MODELO,
        messages=mensajes,
        temperature=0.6,
        max_completion_tokens=2048,
        stream=True,
    )
    for fragmento in flujo:
        if not fragmento.choices:
            continue
        texto = fragmento.choices[0].delta.content
        if texto:
            yield texto


def mensaje_de_error(error: Exception) -> str:
    """Convierte excepciones de la API en mensajes comprensibles en español."""
    if isinstance(error, AuthenticationError):
        return (
            "🔑 La clave de API no es válida o fue rechazada por Groq. "
            "Verifica el valor de `LLAVE_PROFESOR`."
        )
    if isinstance(error, RateLimitError):
        return (
            "⏳ Se alcanzó el límite de uso de la API. Espera un momento e "
            "inténtalo de nuevo."
        )
    if isinstance(error, APITimeoutError):
        return "⌛ La conexión con Groq tardó demasiado. Inténtalo de nuevo."
    if isinstance(error, APIConnectionError):
        return (
            "🌐 No fue posible conectar con Groq. Revisa tu conexión a "
            "internet e inténtalo otra vez."
        )
    if isinstance(error, APIStatusError):
        return (
            f"❌ Groq respondió con un error (código {error.status_code}). "
            "Inténtalo nuevamente en unos instantes."
        )
    return f"❌ Ocurrió un error inesperado: {error}"


# ----------------------------------------------------------------------------
# Interfaz
# ----------------------------------------------------------------------------
st.title("🎓 Asistente Virtual de la Clase")
st.caption(f"Pregúntame lo que necesites sobre la clase · Modelo: {MODELO}")

with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()
    st.markdown(
        "Este asistente recuerda lo conversado durante tu sesión. "
        "Si cierras o recargas la página, el historial se reinicia."
    )

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

cliente = obtener_cliente()

# Mostrar el historial de la conversación.
for mensaje in st.session_state.mensajes:
    avatar = "🧑‍🎓" if mensaje["role"] == "user" else "🎓"
    with st.chat_message(mensaje["role"], avatar=avatar):
        st.markdown(mensaje["content"])

# Entrada del usuario.
pregunta = st.chat_input(
    "Escribe tu pregunta aquí...",
    disabled=cliente is None,
)

if pregunta and cliente is not None:
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(pregunta)

    with st.chat_message("assistant", avatar="🎓"):
        try:
            respuesta = st.write_stream(
                generar_respuesta(cliente, st.session_state.mensajes)
            )
        except Exception as error:  # noqa: BLE001
            st.error(mensaje_de_error(error))
            # Se retira la pregunta fallida para mantener el historial coherente.
            st.session_state.mensajes.pop()
        else:
            if respuesta and str(respuesta).strip():
                st.session_state.mensajes.append(
                    {"role": "assistant", "content": str(respuesta)}
                )
            else:
                st.warning(
                    "El modelo no devolvió ninguna respuesta. "
                    "Intenta reformular tu pregunta."
                )
                st.session_state.mensajes.pop()
