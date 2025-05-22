import io
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import pandas as pd

app = FastAPI(
    title="Analizador Léxico API",
    description="API para análisis léxico de expresiones aritméticas",
    version="1.0.0"
)

class ExpresionRequest(BaseModel):
    expresion: str

from typing import Optional

class AnalisisResponse(BaseModel):
    error: Optional[str] = None
    tokens_image: Optional[str] = None
    symbols_image: Optional[str] = None
    types_image: Optional[str] = None

def generar_imagen_tabla(df: pd.DataFrame, titulo: str) -> str:
    # Set style to minimalist
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Create figure with white background
    plt.figure(figsize=(10, 6), facecolor='white')
    plt.axis('tight')
    plt.axis('off')
    
    # Create table with minimalist design
    tabla = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        edges='horizontal',  # Only show horizontal lines
        bbox=[0.1, 0.1, 0.8, 0.8]  # Adjust table size and position
    )
    
    # Style the table
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    
    # Style header
    for k, cell in tabla._cells.items():
        cell.set_edgecolor('white')
        if k[0] == 0:  # Header styling
            cell.set_facecolor('#f0f0f0')
            cell.set_text_props(weight='bold')
        else:  # Content styling
            cell.set_facecolor('white')
    
    # Add title with minimal styling
    plt.title(titulo, pad=20, fontsize=12, fontweight='bold')
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    
    # Convert to base64
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return img_base64

def analisis_lexico(expresion: str) -> Tuple[str | None, List[Dict], List[Dict], List[Dict]]:
    if not expresion.strip():
        return "Error: La expresión está vacía", [], [], []

    tokens = []
    simbolos = []
    tipos = []
    i = 0
    ultimo_operador = False
    token_id = 1
    simbolos_unicos = {}
    dir_counter = 1

    # Validate input string for invalid characters first
    for pos, char in enumerate(expresion):
        if not (char.isdigit() or char in '+-*/ ' or char.isspace()):
            return f'Error: Carácter no válido "{char}" encontrado en la posición {pos + 1}', [], [], []

    while i < len(expresion):
        char = expresion[i]

        if char.isspace():
            i += 1
            continue

        if char.isdigit():
            numero = char
            start_pos = i
            i += 1
            while i < len(expresion) and expresion[i].isdigit():
                numero += expresion[i]
                i += 1
            
            if numero not in simbolos_unicos:
                simbolos_unicos[numero] = f"dir_{dir_counter}"
                dir_counter += 1

            tokens.append({
                "ID": token_id,
                "Token": numero,
                "Tipo": "Número",
                "Posición": start_pos + 1
            })
            simbolos.append({
                "ID": token_id, 
                "Símbolo": numero, 
                "Categoría": "Literal",
                "Dirección": simbolos_unicos[numero],
                "Tipo": "entero"  # Added to match requirements
            })
            tipos.append({
                "ID": token_id,
                "Símbolo": numero,  # Changed to match requirements
                "Tipo": "entero",
                "Referencia": simbolos_unicos[numero]  # Added reference to symbol table
            })
            token_id += 1
            ultimo_operador = False
        elif char in '+-*/':
            if ultimo_operador:
                return f'Error: Operadores consecutivos encontrados en la posición {i + 1}', [], [], []
            tokens.append({
                "ID": token_id,
                "Token": char,
                "Tipo": "Operador",
                "Posición": i + 1
            })
            simbolos.append({
                "ID": token_id,
                "Símbolo": char,
                "Categoría": "Operador"
            })
            tipos.append({
                "ID": token_id,
                "Símbolo": char,
                "Tipo": "operator"
            })
            token_id += 1
            ultimo_operador = True
            i += 1

    if ultimo_operador:
        return 'Error: La expresión no puede terminar con un operador', [], [], []

    return None, tokens, simbolos, tipos

@app.post("/analizar", response_model=AnalisisResponse)
def analizar_expresion(request: ExpresionRequest):
    try:
        error, tokens, simbolos, tipos = analisis_lexico(request.expresion)
        if error:
            return {"error": error, "tokens_image": None, "symbols_image": None, "types_image": None}
        
        # Generar DataFrames
        df_tokens = pd.DataFrame(tokens)
        df_simbolos = pd.DataFrame(simbolos)
        df_tipos = pd.DataFrame(tipos)
        
        # Generar imágenes de las tablas
        tokens_img = generar_imagen_tabla(df_tokens, "Tabla de Tokens")
        simbolos_img = generar_imagen_tabla(df_simbolos, "Tabla de Símbolos")
        tipos_img = generar_imagen_tabla(df_tipos, "Tabla de Tipos")
        
        return {
            "error": None,
            "tokens_image": tokens_img,
            "symbols_image": simbolos_img,
            "types_image": tipos_img
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)