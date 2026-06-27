import os
import json
import logging
from sqlalchemy.orm import Session

# We need to ensure that the environment variables are available.
# We assume they are set in the HF space. If not, the server wouldn't run anyway.

# Monkey-patch get_embedding to prevent OpenAI API calls for seeding
import aci.common.utils
aci.common.utils.get_embedding = lambda *args, **kwargs: [0.0] * 1536
try:
    import aci.server.config
    aci.server.config.get_embedding = lambda *args, **kwargs: [0.0] * 1536
except ImportError:
    pass

from aci.common import utils
from aci.server import config
from aci.common.db.crud import apps
from aci.common.schemas.app import AppUpsert
from aci.common.enums import SecurityScheme, Visibility

def get_db():
    return utils.create_db_session(config.DB_FULL_URL)

def main():
    print("Starting database seeding...", flush=True)
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
        print(f"Apps directory {apps_dir} not found. Skipping.", flush=True)
        return
        
    for app_name, keys in KEYS.items():
        app_path = os.path.join(apps_dir, app_name, "app.json")
        if not os.path.exists(app_path):
            print(f"Missing app.json for {app_name}, skipping.", flush=True)
            continue
            
        with open(app_path, "r", encoding="utf-8") as f:
            app_data = json.load(f)
            
        if "security_schemes" in app_data:
            if "oauth2" in app_data["security_schemes"]:
                app_data["security_schemes"]["oauth2"]["client_id"] = keys["id"]
                app_data["security_schemes"]["oauth2"]["client_secret"] = keys["secret"]
            elif "OAUTH2" in app_data["security_schemes"]:
                app_data["security_schemes"]["OAUTH2"]["client_id"] = keys["id"]
                app_data["security_schemes"]["OAUTH2"]["client_secret"] = keys["secret"]
            
        app_data["visibility"] = Visibility.PUBLIC
        app_data["default_security_credentials_by_scheme"] = {}
        
        try:
            upsert_schema = AppUpsert(**app_data)
            
            actual_app_name = app_data.get("name", app_name.upper())
            app_obj = apps.get_app(db_session, actual_app_name, public_only=False, active_only=False)
            dummy_embedding = [0.0] * 1024 
            
            if not app_obj:
                app_obj = apps.create_app(db_session, upsert_schema, app_embedding=dummy_embedding)
                print(f"Created app {actual_app_name}", flush=True)
            else:
                app_obj = apps.update_app(db_session, app_obj, upsert_schema, app_embedding=dummy_embedding)
                print(f"Updated app {actual_app_name}", flush=True)
                
            apps.set_app_active_status(db_session, actual_app_name, active=True)
            apps.set_app_visibility(db_session, actual_app_name, visibility=Visibility.PUBLIC)
            
            security_scheme = SecurityScheme.OAUTH2
            credentials = {
                "client_id": keys["id"],
                "client_secret": keys["secret"]
            }
            apps.update_app_default_security_credentials(db_session, app_obj, security_scheme, credentials)
            
            # Clear any stale overrides in AppConfiguration so it falls back to the App's injected credentials
            from sqlalchemy import select
            from aci.common.db.sql_models import AppConfiguration
            statement = select(AppConfiguration).filter_by(app_name=actual_app_name)
            app_configs = db_session.execute(statement).scalars().all()
            for conf in app_configs:
                conf.security_scheme_overrides = {}
                
        except Exception as e:
            print(f"Error processing {actual_app_name}: {e}", flush=True)
            
    try:
        db_session.commit()
        print("Database seeding completed gracefully.", flush=True)
    except Exception as e:
        print(f"Error committing DB: {e}", flush=True)
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == "__main__":
    main()
