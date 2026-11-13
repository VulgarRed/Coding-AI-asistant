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
    "🐍 Escribir código": "Escribe en Python una función que valide contraseñas seguras y explícala.",
    "🔧 Modificar código": "Convierte este código de Python a JavaScript:\n\n```python\ndef suma(a, b):\n    return a + b\n```",
    "🛡️ Práctica de ciberseguridad": "Propón un ejercicio práctico de inyección SQL en un laboratorio propio y cómo corregirlo.",
    "🧩 Resolver un problema": "Mi aplicación web guarda contraseñas en texto plano. ¿Cómo lo soluciono paso a paso?",
}

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Asistente de Programación con IA",
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
        f"⚠️ No se encontró una clave de API válida en `{NOMBRE_SECRETO}`."
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
    st.header("⚙️ Opciones")
    temperatura = st.slider(
        "Creatividad de las respuestas",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Valores bajos dan respuestas más precisas; valores altos, más creativas.",
    )
    if st.button("🗑️ Borrar conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    st.divider()
    st.subheader("💡 Ejemplos rápidos")
    ejemplo_elegido = None
    for etiqueta, texto in SUGERENCIAS.items():
        if st.button(etiqueta, use_container_width=True):
            ejemplo_elegido = texto

    st.divider()
    st.caption(f"Modelo: `{MODELO}` · Proveedor: Groq")
    st.caption(
        "Uso educativo y defensivo en ciberseguridad. "
        "Practica solo en sistemas propios o con autorización."
    )

# ---------------------------------------------------------------------------
# Interfaz principal
# ---------------------------------------------------------------------------
st.title("💻 Asistente de Programación con IA")
st.caption(
    "Pregunta en lenguaje natural: genera y modifica código en cualquier "
    "lenguaje y practica resolución de problemas de ciberseguridad."
)

api_key = obtener_api_key()
if api_key is None:
    mostrar_error_configuracion()
    st.stop()

try:
    cliente = crear_cliente(api_key)
except Exception as error:
    st.error(f"❌ No se pudo crear el cliente de Groq: {error}")
    st.stop()

# Mostrar el historial de la conversación
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

if not st.session_state.mensajes:
    st.info("👋 ¡Hola! Escribe tu pregunta abajo o elige un ejemplo en la barra lateral.")

# Entrada del usuario
entrada = st.chat_input("Escribe tu pregunta sobre código o ciberseguridad...")
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
            st.error("🔑 La clave de API no es válida o fue revocada. Revisa tu configuración.")
        except RateLimitError:
            st.session_state.mensajes.pop()
            st.error("⏳ Se alcanzó el límite de uso de la API. Espera un momento e inténtalo de nuevo.")
        except APIConnectionError:
            st.session_state.mensajes.pop()
            st.error("🌐 No se pudo conectar con Groq. Revisa tu conexión a internet e inténtalo de nuevo.")
        except APIStatusError as error:
            st.session_state.mensajes.pop()
            st.error(f"❌ Groq devolvió un error (código {error.status_code}). Inténtalo de nuevo.")
        except Exception as error:
            st.session_state.mensajes.pop()
            st.error(f"❌ Ocurrió un error inesperado: {error}")
