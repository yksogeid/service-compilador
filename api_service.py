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
    tokens: List[Tuple[str, str]]
    tabla_simbolos: Dict[str, str]
    tabla_tipos: Dict[str, str]
    imagenes: Dict[str, str]
    errores: List[Tuple[str, int]]

def analisis_lexico(expresion: str):
    tokens = []
    tabla_simbolos = {}
    tabla_tipos = {}
    errores = []
    direccion_counter = 1
    i = 0

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
            tokens.append(('NUMERO', numero))

            if numero not in tabla_simbolos:
                tabla_simbolos[numero] = f'dir_{direccion_counter}'
                tabla_tipos[numero] = 'entero'
                direccion_counter += 1
        elif char in '+-*/':
            tokens.append(('OPERADOR', char))
            i += 1
        else:
            errores.append((char, i))
            i += 1

    return tokens, tabla_simbolos, tabla_tipos, errores

def generar_tabla_imagen_base64(data, columnas, titulo) -> str:
    df = pd.DataFrame(data, columns=columnas)
    fig, ax = plt.subplots(figsize=(6, 2 + len(data) * 0.5))
    ax.axis('off')

    tabla = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center',
        cellLoc='center',
        colColours=["#4682B4"] * len(columnas),
        cellColours=[["#F0F8FF"] * len(columnas) for _ in range(len(data))]
    )

    tabla.auto_set_font_size(False)
    tabla.set_fontsize(12)
    tabla.scale(1.2, 1.2)

    plt.title(titulo, fontsize=16, fontweight='bold', pad=20, color='#333333')
    plt.figtext(0.5, 0.02, "copyright yksogeid", wrap=True,
                horizontalalignment='center', fontsize=10, color='gray', style='italic')

    # Guardar la imagen en un buffer de memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    buf.seek(0)
    
    # Convertir a base64
    imagen_base64 = base64.b64encode(buf.getvalue()).decode()
    return imagen_base64

@app.post("/analizar", response_model=AnalisisResponse)
def analizar_expresion(request: ExpresionRequest):
    try:
        tokens, simbolos, tipos, errores = analisis_lexico(request.expresion)
        
        # Generar imágenes en base64
        imagenes = {}
        if not errores:
            # Generar imagen de tokens
            imagenes['tokens'] = generar_tabla_imagen_base64(
                tokens, ["TIPO", "VALOR"], "Tokens Identificados")
            
            # Generar imagen de tabla de símbolos
            simbolos_data = [(k, v) for k, v in simbolos.items()]
            imagenes['simbolos'] = generar_tabla_imagen_base64(
                simbolos_data, ["Símbolo", "Dirección"], "Tabla de Símbolos")
            
            # Generar imagen de tabla de tipos
            tipos_data = [(k, v) for k, v in tipos.items()]
            imagenes['tipos'] = generar_tabla_imagen_base64(
                tipos_data, ["Símbolo", "Tipo"], "Tabla de Tipos")
        
        return {
            "tokens": tokens,
            "tabla_simbolos": simbolos,
            "tabla_tipos": tipos,
            "imagenes": imagenes,
            "errores": errores
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)