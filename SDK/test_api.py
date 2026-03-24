import requests
import json

# The URL of your locally running FastAPI Docker container
API_URL = "http://localhost:8000/generate-and-verify"

# Mock payload mirroring what the Lovable UI will send
payload = {
    "wavelength_nm": 1550.0,
    "cladding": "SiO2",
    "target_n_eff": 2.45,
    "requested_etch_depth_nm": 220.0,
    "solver_choice": "lumerical"
}

print("🚀 Sending request to Precision with Light Backend...")

try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status() # Raise an exception for bad status codes (e.g., 500 or 404)
    
    data = response.json()
    
    print("\n✅ Success! Received response from the Trust Layer:")
    
    # Extracting the most important pieces for the CTO demo
    status = data.get("status")
    fidelity = data.get("physics_verification", {}).get("fidelity_score")
    solver = data.get("physics_verification", {}).get("solver_engine")
    logs = data.get("pipeline_diagnostics", [])
    
    print(f"Status: {status}")
    print(f"Solver Engine: {solver}")
    print(f"Fidelity Score: {fidelity}")
    print("\nPipeline Logs:")
    for log in logs:
        print(f" - {log}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error: Is your Docker container running? Try running 'docker-compose up -d'")
except Exception as e:
    print(f"\n❌ An error occurred: {e}")
    if 'response' in locals() and response.status_code != 200:
        print(f"Server response details: {response.text}")
