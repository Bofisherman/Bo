import os
from dotenv import load_dotenv

# ✅ Load .env first thing in the file
load_dotenv()
print("🚨 DEBUG: MAIL_PASSWORD =", os.environ.get("MAIL_PASSWORD"))

# ✅ NOW import anything from fishcore
from fishcore.init_db import initialize_database
from fishcore import create_app

initialize_database()
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10001))
    app.run(host="0.0.0.0", port=port, debug=True)
