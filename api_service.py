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

    while i < len(expresion):
        char = expresion[i]

        if char.isspace():
            i += 1
            continue

        # Validar caracteres permitidos
        if not (char.isdigit() or char in '+-*/' or char.isspace()):
            return f'Error: Carácter no válido "{char}" encontrado en la posición {i + 1}', [], [], []

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

    # Modificar la estructura de tokens
    tokens_formatted = []
    for token in tokens:
        if token["Tipo"] == "Número":
            tokens_formatted.append({
                "Token": f"[TIPO: {token['Tipo'].upper()}, VALOR: {token['Token']}]"
            })
        else:
            tokens_formatted.append({
                "Token": f"[TIPO: {token['Tipo'].upper()}, VALOR: {token['Token']}]"
            })

    # Modificar la estructura de símbolos (solo números únicos)
    simbolos_formatted = []
    simbolos_vistos = set()
    for s in simbolos:
        if s["Categoría"] == "Literal" and s["Símbolo"] not in simbolos_vistos:
            simbolos_formatted.append({
                "Símbolo": s["Símbolo"],
                "Dirección": s["Dirección"]
            })
            simbolos_vistos.add(s["Símbolo"])

    # Modificar la estructura de tipos (solo números únicos)
    tipos_formatted = []
    tipos_vistos = set()
    for t in tipos:
        if t["Tipo"] == "entero" and t["Símbolo"] not in tipos_vistos:
            tipos_formatted.append({
                "Símbolo": t["Símbolo"],
                "Tipo": t["Tipo"]
            })
            tipos_vistos.add(t["Símbolo"])

    return None, tokens_formatted, simbolos_formatted, tipos_formatted

def generar_imagen_tabla(df: pd.DataFrame, titulo: str) -> str:
    # Definir colores para el diseño minimalista moderno
    colors = {
        'background': '#f8f9fa',  # Fondo suave
        'header': '#4361ee',      # Azul moderno
        'header_text': '#ffffff',  # Texto blanco
        'border': '#e9ecef',      # Bordes sutiles
        'cell': '#ffffff',        # Celdas blancas
        'title': '#2b2d42',      # Título oscuro elegante
        'text': '#495057'         # Texto gris oscuro
    }
    
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 7), facecolor=colors['background'])
    plt.axis('tight')
    plt.axis('off')
    
    # Configuración común de la tabla
    table_params = {
        'cellText': df.values,
        'loc': 'center',
        'bbox': [0.05, 0.05, 0.9, 0.85],  # Mejor uso del espacio
        'cellLoc': 'left' if titulo == "Tabla de Tokens" else 'center'
    }
    
    if titulo != "Tabla de Tokens":
        table_params['colLabels'] = df.columns
    
    tabla = plt.table(**table_params)
    
    if titulo == "Tabla de Tokens":
        tabla.auto_set_column_width([0])
    
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)  # Tamaño de fuente más legible
    
    # Estilizar la tabla con diseño moderno
    for k, cell in tabla._cells.items():
        # Eliminar bordes de celdas para un look más limpio
        cell.set_edgecolor(colors['border'])
        cell.set_linewidth(0.5)  # Bordes más finos
        
        # Configurar texto
        cell.set_text_props(color=colors['text'], fontname='DejaVu Sans')
        
        # Estilizar encabezados
        if k[0] == 0 and titulo != "Tabla de Tokens":
            cell.set_facecolor(colors['header'])
            cell.set_text_props(weight='bold', color=colors['header_text'])
            cell.set_alpha(0.9)  # Transparencia sutil
        else:
            cell.set_facecolor(colors['cell'])
            if titulo == "Tabla de Tokens":
                cell._text.set_horizontalalignment('left')
    
    # Título con estilo moderno
    plt.title(titulo, pad=30, fontsize=14, fontweight='bold', 
              color=colors['title'], fontname='DejaVu Sans')
    plt.tight_layout()  # Ajuste automático del layout
    
    # Guardar con fondo transparente
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300, 
                facecolor=colors['background'], edgecolor='none')
    plt.close()
    
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return img_base64

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