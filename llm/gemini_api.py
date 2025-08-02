import requests
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv() 

# Obtener la API key desde el archivo .env
api_key = os.getenv("GEMINI_API_KEY")

# Verificar que la API key esté configurada
if not api_key:
    raise ValueError("No se encontró GEMINI_API_KEY en las variables de entorno. Asegúrate de tener un archivo .env con tu API key.")

# URL de la API de Gemini (URL corregida)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

def get_recommendation(prompt):
    """
    Envía un prompt a la API de Gemini y obtiene una recomendación financiera
    
    Args:
        prompt (str): El prompt construido por prompt_builder
    
    Returns:
        dict: Recomendación financiera con estructura {title, desc, type} o None si hay error
    """
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 2048,
            "stopSequences": []
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }

    params = {
        "key": api_key
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=body)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Verificar si hay contenido en la respuesta
        if 'candidates' not in response_data or not response_data['candidates']:
            print("❌ No se recibió respuesta válida de la API de Gemini")
            return None
        
        if not response_data['candidates'][0].get('content', {}).get('parts'):
            print("❌ Respuesta de Gemini vacía o bloqueada por filtros de seguridad")
            return None
        
        text_output = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # Parsear la respuesta JSON
        recommendation = parse_gemini_response(text_output)
        
        if recommendation and validate_recommendation(recommendation):
            return recommendation
        else:
            print(f"❌ Respuesta de Gemini no válida: {text_output}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición HTTP a Gemini: {e}")
        return None
    except KeyError as e:
        print(f"❌ Error al procesar la respuesta de Gemini: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado con Gemini API: {e}")
        return None

def parse_gemini_response(text_output):
    """
    Parsea la respuesta de texto de Gemini a un diccionario
    
    Args:
        text_output (str): Texto de respuesta de Gemini
    
    Returns:
        dict: Diccionario con title, desc y type o None si no se puede parsear
    """
    try:
        # Limpiar el texto
        cleaned_text = text_output.strip()
        
        # Si contiene bloques de código markdown, extraer el JSON
        if "```json" in cleaned_text:
            start = cleaned_text.find("```json") + 7
            end = cleaned_text.find("```", start)
            if end != -1:
                cleaned_text = cleaned_text[start:end].strip()
        elif "```" in cleaned_text:
            start = cleaned_text.find("```") + 3
            end = cleaned_text.rfind("```")
            if end != -1 and end > start:
                cleaned_text = cleaned_text[start:end].strip()
        
        # Intentar parsear como JSON directamente
        try:
            recommendation = json.loads(cleaned_text)
            return recommendation
        except json.JSONDecodeError:
            # Si falla, intentar extraer JSON de una respuesta más compleja
            return extract_json_from_text(cleaned_text)
            
    except Exception as e:
        print(f"Error al parsear respuesta: {e}")
        return None

def extract_json_from_text(text):
    """
    Intenta extraer un objeto JSON válido de un texto que puede contener otros contenidos
    
    Args:
        text (str): Texto que puede contener JSON
    
    Returns:
        dict: Objeto JSON extraído o None
    """
    # Buscar patrones de JSON en el texto
    import re
    
    # Buscar un objeto JSON que comience con { y termine con }
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text)
    
    for match in matches:
        try:
            obj = json.loads(match)
            # Verificar que tenga la estructura esperada
            if isinstance(obj, dict) and all(key in obj for key in ['title', 'desc', 'type']):
                return obj
        except json.JSONDecodeError:
            continue
    
    return None

def validate_recommendation(recommendation):
    """
    Valida que la recomendación tenga la estructura correcta
    
    Args:
        recommendation (dict): Recomendación a validar
    
    Returns:
        bool: True si es válida, False en caso contrario
    """
    if not isinstance(recommendation, dict):
        return False
    
    required_fields = ["title", "desc", "type"]
    valid_types = ["excessive_expenses", "recurrent_expenses", "savings_opportunities", "no_transactions"]
    
    # Verificar que tenga todos los campos requeridos
    if not all(field in recommendation for field in required_fields):
        missing = [f for f in required_fields if f not in recommendation]
        print(f"❌ Faltan campos requeridos: {missing}")
        return False
    
    # Verificar que el tipo sea válido
    if recommendation["type"] not in valid_types:
        print(f"❌ Tipo inválido: {recommendation['type']}. Tipos válidos: {valid_types}")
        return False
    
    # Verificar que los campos no estén vacíos
    for field in required_fields:
        if not isinstance(recommendation[field], str) or not recommendation[field].strip():
            print(f"❌ Campo '{field}' está vacío o no es string válido")
            return False
    
    return True

def test_gemini_connection():
    """
    Función para probar la conexión con la API de Gemini
    """
    test_prompt = '''
You are a smart financial assistant. Generate a test recommendation.

Return only a JSON object with this structure:
{
  "title": "Conexión exitosa",
  "desc": "La API de Gemini está funcionando correctamente",
  "type": "no_transactions"
}
'''
    
    print("🔄 Probando conexión con la API de Gemini...")
    result = get_recommendation(test_prompt)
    
    if result:
        print("✅ Conexión exitosa con Gemini!")
        print(f"Respuesta de prueba: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return True
    else:
        print("❌ Error en la conexión con Gemini")
        return False

# Función para testing (solo se ejecuta si este archivo se ejecuta directamente)
if __name__ == "__main__":
    test_gemini_connection()