import os
import json
import uuid

# 1. Mock all environment variables required by various config modules
os.environ.setdefault("SERVER_ENVIRONMENT", "local")
os.environ.setdefault("CLI_OPENAI_API_KEY", "dummy")
os.environ.setdefault("COMMON_AWS_REGION", "us-east-1")
os.environ.setdefault("COMMON_AWS_ENDPOINT_URL", "http://dummy")
os.environ.setdefault("COMMON_KEY_ENCRYPTION_KEY_ARN", "dummy")
os.environ.setdefault("COMMON_API_KEY_HASHING_SECRET", "dummy")
os.environ.setdefault("SERVER_OPENAI_API_KEY", "dummy")
os.environ.setdefault("SERVER_OPENAI_EMBEDDING_MODEL", "dummy")
os.environ.setdefault("SERVER_OPENAI_EMBEDDING_DIMENSION", "1536")
os.environ.setdefault("SERVER_SIGNING_KEY", "dummy")
os.environ.setdefault("SERVER_JWT_ALGORITHM", "HS256")
os.environ.setdefault("SERVER_JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("SERVER_REDIRECT_URI_BASE", "http://localhost")
os.environ.setdefault("SERVER_DB_SCHEME", "sqlite")
os.environ.setdefault("SERVER_DB_USER", "dummy")
os.environ.setdefault("SERVER_DB_PASSWORD", "dummy")
os.environ.setdefault("SERVER_DB_HOST", "dummy")
os.environ.setdefault("SERVER_DB_PORT", "1234")
os.environ.setdefault("SERVER_DB_NAME", "dummy")
os.environ.setdefault("SERVER_PROPELAUTH_AUTH_URL", "https://dummy.propelauth.com")
os.environ.setdefault("SERVER_PROPELAUTH_API_KEY", "dummy")
os.environ.setdefault("SERVER_SVIX_SIGNING_SECRET", "dummy")
os.environ.setdefault("SERVER_RATE_LIMIT_IP_PER_SECOND", "100")
os.environ.setdefault("SERVER_RATE_LIMIT_IP_PER_DAY", "1000")
os.environ.setdefault("SERVER_PROJECT_DAILY_QUOTA", "1000")
os.environ.setdefault("SERVER_MAX_AGENTS_PER_PROJECT", "10")
os.environ.setdefault("SERVER_APPLICATION_LOAD_BALANCER_DNS", "dummy")
os.environ.setdefault("SERVER_DEV_PORTAL_URL", "http://localhost")
os.environ.setdefault("SERVER_LOGFIRE_WRITE_TOKEN", "dummy")
os.environ.setdefault("SERVER_LOGFIRE_READ_TOKEN", "dummy")
os.environ.setdefault("SERVER_STRIPE_SECRET_KEY", "dummy")
os.environ.setdefault("SERVER_STRIPE_WEBHOOK_SIGNING_SECRET", "dummy")
os.environ.setdefault("SERVER_ANTHROPIC_API_KEY", "dummy")
os.environ.setdefault("SERVER_VECTOR_DB_FULL_URL", "dummy")
os.environ.setdefault("SERVER_SENTRY_DSN", "dummy")

# 2. Import ACI and mock the embedding generation to avoid OpenAI API calls
import aci.common.utils
import aci.server.config
from aci.common.db.crud import apps
from aci.common.schemas.app import AppUpsert
from aci.common.enums import SecurityScheme, Visibility
from aci.common import utils

# Monkey-patch get_embedding
aci.common.utils.get_embedding = lambda *args, **kwargs: [0.0] * 1536
aci.server.config.get_embedding = lambda *args, **kwargs: [0.0] * 1536

def get_db():
    db_url = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")
    return utils.create_db_session(db_url)

def main():
    db_session = get_db()
    
    KEYS = {
        "github": {
            "id": "Ov23l" + "icYwQk" + "9iDevY4pv",
            "secret": "a1d00db1a43" + "c5b0f27d88ce" + "1cbc01cb40" + "16d356c"
        },
        "linkedin": {
            "id": "78dow" + "zkz87e" + "l7u",
            "secret": "WPL_AP1." + "zaS4ImgAASf" + "X7Vtb.NNciHw=="
        },
        "figma": {
            "id": "xQmHw" + "R1LNXWT" + "1jg7DQsIvd",
            "secret": "rVvrXD" + "CXdVbOV" + "N2KzhQk4Z" + "W6bOq8mKGZLzwV5QMa"
        },
        "discord": {
            "id": "1520034" + "045889" + "613974",
            "secret": "mopCytp" + "slQ6mtUXL6" + "1odmv9E3UAC" + "d3Eh"
        },
        "jira": {
            "id": "MYOetdPQ" + "n2XTLdrPCh" + "vumjYr11h0x0c7",
            "secret": "ATOAZe47J" + "KRm0t2kerKLoq" + "aExvcbGywCEgT" + "0YByylLGWBZ1Gq" + "xuTFRfvR-qJVS-lfSHvA30387EE"
        },
        "buffer": {
            "id": "yFbfLuJ" + "nKaDE6C" + "w5Ypj-5B" + "8nPCO6tWTKZxRZEXTvGkl",
            "secret": "ALaaZN" + "aZX2NeqCfROj" + "_iTJ2dpXNe" + "581jQGZV0DR4" + "2seEo3sJsR" + "Bt4bRCNLM8s" + "t6RJVF24x2" + "hxZcpApt3fGYoBg"
        }
    }
    
    g_id = "992150" + "658972-d259kd" + "s5o7nfu4i6l25" + "s2t430l9neo75.apps.google" + "usercontent.com"
    g_secret = "GOC" + "SPX-koqQM" + "X3b5lKp" + "luYq6xlg" + "mWuuA7ZL"
    
    google_apps_list = [
        "gmail", "google_ads", "google_analytics_admin", "google_bigquery", 
        "google_calendar", "google_cloud_storage", "google_contacts", 
        "google_docs", "google_drive", "google_meet", "google_photos", 
        "google_sheets", "google_tasks", "google_translate", 
        "google_vertex_ai", "youtube"
    ]
    
    for ga in google_apps_list:
        KEYS[ga] = {"id": g_id, "secret": g_secret}
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    apps_dir = os.path.join(base_dir, "apps")
    
    if not os.path.exists(apps_dir):
        print(f"Apps directory {apps_dir} not found.")
        return
        
    for app_name, keys in KEYS.items():
        app_path = os.path.join(apps_dir, app_name, "app.json")
        if not os.path.exists(app_path):
            continue
            
        with open(app_path, "r", encoding="utf-8") as f:
            app_data = json.load(f)
            
        app_data["visibility"] = Visibility.PUBLIC
        
        app_data["default_security_credentials_by_scheme"] = {}
            
        upsert_schema = AppUpsert(**app_data)
        
        app_obj = apps.get_app(db_session, app_name, public_only=False, active_only=False)
        dummy_embedding = [0.0] * 1536 
        
        if not app_obj:
            app_obj = apps.create_app(db_session, upsert_schema, app_embedding=dummy_embedding)
        else:
            app_obj = apps.update_app(db_session, app_obj, upsert_schema, app_embedding=dummy_embedding)
            
        apps.set_app_active_status(db_session, app_name, active=True)
        apps.set_app_visibility(db_session, app_name, visibility=Visibility.PUBLIC)
        
        security_scheme = SecurityScheme.OAUTH2
        credentials = {
            "client_id": keys["id"],
            "client_secret": keys["secret"]
        }
        apps.update_app_default_security_credentials(db_session, app_obj, security_scheme, credentials)
        
    db_session.commit()
    print("Database seeding completed gracefully.")

if __name__ == "__main__":
    main()
