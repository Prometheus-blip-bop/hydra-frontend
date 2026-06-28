import os
import json

def reveal_environment_variables():
    # Gather all environment variables
    env_vars = dict(os.environ)
    
    # Print them in a formatted JSON way
    print("=== ENVIRONMENT VARIABLES ===")
    print(json.dumps(env_vars, indent=4))

if __name__ == "__main__":
    reveal_environment_variables()
