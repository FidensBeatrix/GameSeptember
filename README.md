# Kinetic Sand PAC-MAN — Streamlit

Browser version of the Kinetic Sand castle game.

## Files

- `app.py` — Streamlit app + browser game
- `RATeamLogo.png` — put your logo beside `app.py`
- `requirements.txt`
- `.streamlit/secrets.toml.example` — example login configuration

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

For local login testing, copy:

`.streamlit/secrets.toml.example`

to:

`.streamlit/secrets.toml`

and change the passwords.

**Never upload the real `secrets.toml` file to GitHub.**

## Streamlit Community Cloud

1. Push this folder to GitHub.
2. Create a new Streamlit app from the repository.
3. Main file path: `app.py`
4. In the Streamlit app settings, open **Secrets**.
5. Paste:

```toml
[auth.users]
Venitas = "YOUR_REAL_PASSWORD"
Gondor = "ANOTHER_REAL_PASSWORD"
```

6. Save/reboot the app if requested.

The login page reads those credentials from `st.secrets`.

## Logo

Add your real file named exactly:

`RATeamLogo.png`

to the same repository folder as `app.py`.

It will appear beside the login form.
