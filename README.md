# 🎓 Class Virtual Assistant (Asistente Virtual de la Clase)

A web chat app built with **Python 3.11** and **Streamlit** that uses the
`openai/gpt-oss-20b` model through the **Groq API**. Students can ask questions
in natural language; the app keeps the conversation history during the session
and sends it to the model so it keeps the context.

> The user interface is entirely in **Spanish**, and the assistant answers in English.

## Features

- Chat interface with user and assistant messages.
- Natural-language questions sent to `openai/gpt-oss-20b` via the Groq API.
- Real-time (streaming) responses.
- Conversation history kept in the session and sent to the model on every query
  (the last 20 messages, to avoid exceeding the context window).
- **"Nueva conversación"** button in the sidebar to reset the chat.
- API key loaded from `st.secrets["LLAVE_PROFESOR"]`.
- Clear error messages for:
  - missing secrets file or missing/empty key,
  - invalid API key,
  - rate limits,
  - timeouts and connection problems,
  - other API errors or empty model responses.
- Chat input is disabled while the configuration is invalid.
- A failed question is removed from the history so the conversation stays consistent.
- Runs locally and on Streamlit Community Cloud.

## Project structure

```
.
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml      # Local only, NOT committed to GitHub
```

## Requirements

- Python 3.11
- A Groq API key (https://console.groq.com/keys)

## Running locally

### 1. Create and activate a virtual environment

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt / CMD)**

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
```

> If PowerShell shows *"running scripts is disabled on this system"*, see
> [Troubleshooting](#troubleshooting).

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

Create the file `.streamlit/secrets.toml` (copy the provided `secrets.toml`
template) and add your real key:

```toml
LLAVE_PROFESOR = "your_groq_api_key"
```

### 4. Run the app

```bash
streamlit run app.py
```

## Deploying to Streamlit Community Cloud

1. Push the project to a GitHub repository (the real `secrets.toml` is excluded
   by `.gitignore`).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, choose the repository, the branch and `app.py` as the
   main file.
4. Under **Advanced settings**:
   - Select **Python 3.11**.
   - In **Secrets**, paste:

     ```toml
     LLAVE_PROFESOR = "your_groq_api_key"
     ```
5. Click **Deploy**.

## Troubleshooting

### PowerShell: "running scripts is disabled on this system"

PowerShell's execution policy blocks the virtual environment activation script.
Use any of these options:

- **Allow scripts for your user only (recommended):**

  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **Allow scripts only in the current window:**

  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
  ```

- **Use CMD** and run `.venv\Scripts\activate.bat`.
- **Skip activation** and call the environment's Python directly:

  ```powershell
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  .venv\Scripts\python.exe -m streamlit run app.py
  ```

If your project path contains spaces (for example `AI for Coding`), wrap full
paths in quotes.

### Messages shown by the app

The app interface is in Spanish; this table explains what each message means.

| Message (Spanish) | Likely cause |
|---|---|
| No se encontró el archivo de secretos | `.streamlit/secrets.toml` or the Cloud *Secrets* are missing. |
| Falta la clave `LLAVE_PROFESOR` | The key name is misspelled or does not exist. |
| La clave está vacía | `LLAVE_PROFESOR` has no value. |
| La clave de API no es válida | The key is wrong, expired or revoked. |
| Se alcanzó el límite de uso | Too many requests in a short time; wait and retry. |
| La conexión con Groq tardó demasiado | Request timed out; try again. |
| No fue posible conectar con Groq | Network problem or the service is temporarily unavailable. |
| El modelo no devolvió ninguna respuesta | Empty response; try rephrasing the question. |

## Security

- Never hard-code the API key in the source code.
- Never commit `.streamlit/secrets.toml` to any repository.
- If a key is exposed, revoke it and generate a new one in the Groq console.
