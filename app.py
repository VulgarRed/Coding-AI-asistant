"""
Asistente de Programación con IA
--------------------------------
Aplicación de chat en Streamlit que usa la API de Groq con el modelo
`openai/gpt-oss-20b`. Ayuda a escribir, explicar y modificar código en
cualquier lenguaje, y a practicar resolución de problemas de ciberseguridad.

Requiere Python 3.11, streamlit y groq.
La clave de API se lee de st.secrets["LLAVE_PROFESOR"].
"""

import streamlit as st
from groq import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    Groq,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
MODELO = "openai/gpt-oss-20b"
NOMBRE_SECRETO = "LLAVE_PROFESOR"
MAX_MENSAJES_HISTORIAL = 20  # Cantidad máxima de mensajes enviados como contexto

PROMPT_SISTEMA = (
    "You are an expert assistant in programming and cybersecurity. "
    "ALWAYS answer in English, no matter which language the user writes in, "
    "and keep your answers clear and well organized. "
    "You can write, explain, debug, optimize and modify code in any "
    "programming language (Python, JavaScript, Java, C, C++, C#, Go, Rust, "
    "PHP, SQL, Bash, PowerShell, etc.). When you provide code, make it "
    "complete and functional, inside code blocks with the language "
    "specified, and briefly explain what it does. When the user asks you to "
    "modify code, return the full modified version and summarize the "
    "changes you made.\n\n"
    "In cybersecurity, focus on defensive and educational practice: "
    "problem solving, best-practice suggestions, secure code review, "
    "analysis of common vulnerabilities (OWASP Top 10), hardening, basic "
    "cryptography, CTF-style challenges, personal labs and authorized "
    "environments. When the user presents a problem, propose a step-by-step "
    "solution and suggest improvements. Do not create malware, ransomware or "
    "exploits ready for malicious use, and do not help attack systems "
    "without authorization; in those cases, politely explain why you cannot "
    "help and offer a defensive or educational alternative."
)

SUGERENCIAS = {
    "🐍 "Writing code": "Write a function in Python that validates secure passwords, and explain it."",
    "🔧 "Modify code": "Convert this Python code to JavaScript:\n\n```python\ndef suma(a, b):\n    return a + b\n```",
    "🛡️ "Cybersecurity practice: Propose a practical SQL injection exercise to be carried out in a controlled lab environment, along with how to remediate it."",
    "🧩 "Solving a problem": "My web application stores passwords in plain text. How do I fix this, step by step?"",
}

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Programing Asistant",
    page_icon="💻",
    layout="centered",
)


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def obtener_api_key() -> str | None:
    """Lee la clave de API desde st.secrets. Devuelve None si no es válida."""
    try:
        clave = st.secrets[NOMBRE_SECRETO]
    except Exception:
        return None
    if not isinstance(clave, str):
        return None
    clave = clave.strip()
    if not clave or clave.startswith("PEGA_AQUI"):
        return None
    return clave


@st.cache_resource(show_spinner=False)
def crear_cliente(api_key: str) -> Groq:
    """Crea (y reutiliza) el cliente de Groq."""
    return Groq(api_key=api_key)


def construir_mensajes(historial: list[dict]) -> list[dict]:
    """Arma la lista de mensajes enviada al modelo: sistema + historial reciente."""
    recientes = historial[-MAX_MENSAJES_HISTORIAL:]
    return [{"role": "system", "content": PROMPT_SISTEMA}, *recientes]


def generar_respuesta(cliente: Groq, historial: list[dict], temperatura: float):
    """Generador que entrega la respuesta del modelo por fragmentos (streaming)."""
    flujo = cliente.chat.completions.create(
        model=MODELO,
        messages=construir_mensajes(historial),
        temperature=temperatura,
        max_completion_tokens=4096,
        stream=True,
    )
    for fragmento in flujo:
        if not fragmento.choices:
            continue
        texto = fragmento.choices[0].delta.content
        if texto:
            yield texto


def mostrar_error_configuracion() -> None:
    st.error(
        f"⚠️ No valid API key was found in `{NOMBRE_SECRETO}`."
    )
    st.markdown(
        "**Cómo configurarla:**\n\n"
        "- **Ejecución local:** crea el archivo `.streamlit/secrets.toml` "
        "copiando `secrets.toml.example` y escribe tu clave de Groq.\n"
        "- **Streamlit Community Cloud:** en tu app ve a "
        "*Settings → Secrets* y pega:\n\n"
        f'```toml\n{NOMBRE_SECRETO} = "tu_clave_de_groq"\n```\n'
        "Puedes obtener una clave gratuita en https://console.groq.com/keys"
    )


# ---------------------------------------------------------------------------
# Estado de la sesión
# ---------------------------------------------------------------------------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Options")
    temperatura = st.slider(
        "Creativity of the responses",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Low values ​​yield more precise responses; high values, more creative ones.",
    )
    if st.button("🗑️ Delete conversation", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    st.divider()
    st.subheader("💡 Quick examples")
    ejemplo_elegido = None
    for etiqueta, texto in SUGERENCIAS.items():
        if st.button(etiqueta, use_container_width=True):
            ejemplo_elegido = texto

    st.divider()
    st.caption(f"Modelo: `{MODELO}` · Proveedor: Groq")
    st.caption(
        "Educational and defensive use in cybersecurity. "
        "Practice only on systems you own or have authorization for."
    )

# ---------------------------------------------------------------------------
# Interfaz principal
# ---------------------------------------------------------------------------
st.title("💻 AI Programming Assistant")
st.caption(
    "Ask a question in natural language: Generate and modify code in any language."
    "Language and practice for cybersecurity problem-solving."
)

api_key = obtener_api_key()
if api_key is None:
    mostrar_error_configuracion()
    st.stop()

try:
    cliente = crear_cliente(api_key)
except Exception as error:
    st.error(f"❌ Failed to create the Groq client: {error}")
    st.stop()

# Mostrar el historial de la conversación
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

if not st.session_state.mensajes:
    st.info("👋 Hello! Type your question below or choose an example from the sidebar.")

# Entrada del usuario
entrada = st.chat_input("Write your question about code or cybersecurity...")
consulta = entrada or ejemplo_elegido

if consulta:
    st.session_state.mensajes.append({"role": "user", "content": consulta})
    with st.chat_message("user"):
        st.markdown(consulta)

    with st.chat_message("assistant"):
        try:
            respuesta = st.write_stream(
                generar_respuesta(cliente, st.session_state.mensajes, temperatura)
            )
            st.session_state.mensajes.append(
                {"role": "assistant", "content": respuesta}
            )
        except AuthenticationError:
            st.session_state.mensajes.pop()
            st.error("🔑 The API key is invalid or has been revoked. Check your settings.")
        except RateLimitError:
            st.session_state.mensajes.pop()
            st.error("⏳ The API usage limit has been reached. Please wait a moment and try again.")
        except APIConnectionError:
            st.session_state.mensajes.pop()
            st.error("🌐 Could not connect to Groq. Check your internet connection and try again.")
        except APIStatusError as error:
            st.session_state.mensajes.pop()
            st.error(f"❌ Groq returned an error (código {error.status_code}). Try again.")
        except Exception as error:
            st.session_state.mensajes.pop()
            st.error(f"❌ An unexpected error occurred: {error}")
