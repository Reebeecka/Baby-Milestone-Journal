# Baby-Milestone-Journal

## Security notice

A Gmail app password was previously committed in this repository and **must be treated as compromised**.

1. **Revoke** the old Gmail app password in your Google Account: [Google Account → Security → 2-Step Verification → App passwords](https://myaccount.google.com/apppasswords). Delete the leaked password.
2. **Create a new** app password and put it only in a local `.env` file (see below). Never commit `.env`.
3. **Git history was rewritten** to remove the leaked secret from all commits. Collaborators must **re-clone** this repository (or delete their old clone and fetch the rewritten history). Do not merge or rebase from local branches that still contain the old commits.
4. GitHub may keep unreachable objects from before the rewrite until garbage collection. Ask [GitHub Support to purge cached Git objects](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) if you need them dropped immediately. Revoking the app password is required either way.

## Local setup

```bash
cp .env.example .env
```

Edit `.env` and set at least:

- `SECRET_KEY` — Flask signing key
- `MAIL_USERNAME` — Gmail address used to send mail
- `MAIL_PASSWORD` — new Gmail app password (not your normal Gmail password)

Backend:

```bash
cd backend
pip install -r requirements.txt
python3 app.py
```

Frontend (dev):

```bash
cd frontend
npm install
npm run dev
```

Mail settings are read from the environment at startup. The app will start without `MAIL_PASSWORD`, but password-reset emails will not send until it is set.
