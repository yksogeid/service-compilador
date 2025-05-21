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

class AnalisisResponse(BaseModel):
    error: str | None = None
    tokens_image: str | None = None
    symbols_image: str | None = None
    types_image: str | None = None

def generar_imagen_tabla(df: pd.DataFrame, titulo: str) -> str:
    plt.figure(figsize=(10, 6))
    plt.axis('tight')
    plt.axis('off')
    tabla = plt.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc='center',
                     loc='center')
    plt.title(titulo)
    
    # Guardar la imagen en un buffer de memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    
    # Convertir la imagen a base64
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

    while i < len(expresion):
        char = expresion[i]

        if char.isspace():
            i += 1
            continue

        if char.isdigit():
            numero = char
            i += 1
            while i < len(expresion) and expresion[i].isdigit():
                numero += expresion[i]
                i += 1
            tokens.append({"ID": token_id, "Token": numero, "Tipo": "Número"})
            simbolos.append({"ID": token_id, "Símbolo": numero, "Categoría": "Literal"})
            tipos.append({"ID": token_id, "Tipo": "int", "Descripción": "Número entero"})
            token_id += 1
            ultimo_operador = False
        elif char in '+-*/':
            if ultimo_operador:
                return f'Error: Operadores consecutivos encontrados en la posición {i}', [], [], []
            tokens.append({"ID": token_id, "Token": char, "Tipo": "Operador"})
            simbolos.append({"ID": token_id, "Símbolo": char, "Categoría": "Operador"})
            tipos.append({"ID": token_id, "Tipo": "operator", "Descripción": "Operador aritmético"})
            token_id += 1
            ultimo_operador = True
            i += 1
        else:
            return f'Error: Carácter no válido "{char}" encontrado en la posición {i}', [], [], []

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