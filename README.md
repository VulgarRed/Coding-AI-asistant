# 🎓 Asistente Virtual de la Clase

Aplicación web de chat creada con **Python 3.11** y **Streamlit** que usa el
modelo `openai/gpt-oss-20b` mediante la **API de Groq**. Permite hacer
preguntas en lenguaje natural, mantiene el historial durante la sesión y lo
envía al modelo para conservar el contexto.

## Funcionalidades

- Interfaz de chat completamente en español.
- Respuestas en tiempo real (streaming).
- Historial de la conversación durante la sesión, enviado al modelo en cada consulta.
- Botón para iniciar una nueva conversación.
- Clave de API leída desde `st.secrets["LLAVE_PROFESOR"]`.
- Mensajes claros ante errores de configuración, autenticación, límites de uso o conexión.

## Estructura del proyecto

```
.
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml      # Local, NO se sube a GitHub
```

## Requisitos

- Python 3.11
- Una clave de API de Groq (https://console.groq.com/keys)

## Ejecución local

1. Crea y activa un entorno virtual:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate        # En Windows: .venv\Scripts\activate
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Crea el archivo `.streamlit/secrets.toml` con el siguiente contenido
   (usa tu clave real):

   ```toml
   LLAVE_PROFESOR = "tu_clave_de_groq"
   ```

4. Ejecuta la aplicación:

   ```bash
   streamlit run app.py
   ```

## Publicación en Streamlit Community Cloud

1. Sube el proyecto a un repositorio de GitHub (el archivo `secrets.toml`
   real está excluido por `.gitignore`).
2. Entra a https://share.streamlit.io e inicia sesión con GitHub.
3. Pulsa **Create app**, elige el repositorio, la rama y `app.py` como
   archivo principal.
4. En **Advanced settings**:
   - Selecciona **Python 3.11**.
   - En **Secrets**, pega:

     ```toml
     LLAVE_PROFESOR = "tu_clave_de_groq"
     ```
5. Pulsa **Deploy**.

## Solución de problemas

| Mensaje | Causa probable |
|---|---|
| No se encontró el archivo de secretos | Falta `.streamlit/secrets.toml` o los *Secrets* en la nube. |
| Falta la clave `LLAVE_PROFESOR` | El nombre de la clave está mal escrito o no existe. |
| La clave de API no es válida | La clave es incorrecta, está vencida o fue revocada. |
| Límite de uso alcanzado | Demasiadas consultas en poco tiempo; espera e inténtalo de nuevo. |
| No fue posible conectar con Groq | Problema de red o servicio temporalmente no disponible. |

## Seguridad

- No escribas la clave de API dentro del código.
- No subas `.streamlit/secrets.toml` a ningún repositorio.
- Si una clave se expone, revócala y genera una nueva en la consola de Groq.
