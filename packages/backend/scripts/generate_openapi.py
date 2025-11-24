import json
import os
from backend_projeto.main import app

def generate_openapi_spec():
    """
    Gera a especificação OpenAPI da aplicação FastAPI e a salva em um arquivo.
    """
    # The script is executed from packages/backend, so output to current directory.
    output_path = "openapi.json"
    
    openapi_schema = app.openapi()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
        
    print(f"Especificação OpenAPI salva em: {output_path}")

if __name__ == "__main__":
    generate_openapi_spec()
