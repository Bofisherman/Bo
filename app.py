from fishcore.init_db import initialize_database
from fishcore import create_app

# ✅ First, make sure the DB and tables exist
initialize_database()

# ✅ Then create the app
app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # default fallback
    app.run(host="0.0.0.0", port=port, debug=True)
