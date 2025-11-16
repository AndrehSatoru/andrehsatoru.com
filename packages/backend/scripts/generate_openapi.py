import json
import os
from backend_projeto.main import app

def generate_openapi_spec():
    """
    Gera a especificação OpenAPI da aplicação FastAPI e a salva em um arquivo.
    """
    # Correctly determine the output path relative to the project root
    # The script is in packages/backend/scripts, so we go up two levels
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    output_path = os.path.join(project_root, "packages", "backend", "openapi.json")
    
    openapi_schema = app.openapi()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
        
    print(f"Especificação OpenAPI salva em: {output_path}")

if __name__ == "__main__":
    generate_openapi_spec()
