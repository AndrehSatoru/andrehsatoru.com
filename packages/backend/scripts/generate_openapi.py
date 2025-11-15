import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend_projeto.main import app

def generate_openapi_spec():
    """
    Gera a especificação OpenAPI da aplicação FastAPI e a salva em um arquivo.
    """
    output_dir = os.path.join(os.path.dirname(__file__), '..')
    output_path = os.path.join(output_dir, "openapi.json")
    
    openapi_schema = app.openapi()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
        
    print(f"Especificação OpenAPI salva em: {output_path}")

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), '..', 'src'))
    generate_openapi_spec()
