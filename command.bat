cd starter_v0
py -3 -m venv .venv
call .\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env