from datetime import datetime

def save_recommendation(supabase, user_id, recommendation):
    today_str = datetime.now().strftime("%Y-%m-%d")

    try:
        # 1. Marcar como "útiles" todas las recomendaciones anteriores con useful = NULL
        update_response = supabase.table("recommendations") \
            .update({"useful": True}) \
            .eq("uid", user_id) \
            .is_("useful", None) \
            .execute()

        # En la nueva versión de supabase-py, verificamos si hay data en lugar de status_code
        if update_response.data is not None:
            print(f"🔄 Previous NULL recommendations marked as useful for {user_id}")
        else:
            print(f"ℹ️ No previous NULL recommendations found for {user_id}")

    except Exception as e:
        print(f"⚠️ Error updating old NULL recommendations for {user_id}: {e}")
        # Continuamos con la inserción aunque falle la actualización

    try:
        # 2. Insertar la nueva recomendación
        data = {
            "uid": user_id,
            "title": recommendation["title"],
            "description": recommendation["desc"],
            "useful": None,
            "date": today_str,
            "type": recommendation["type"]
        }

        insert_response = supabase.table("recommendations").insert(data).execute()

        # Verificar si la inserción fue exitosa
        if insert_response.data and len(insert_response.data) > 0:
            print(f"✅ Recommendation saved for {user_id}")
        else:
            print(f"⚠️ Warning: Unexpected response when saving recommendation for {user_id}")
            print(f"Response: {insert_response}")

    except Exception as e:
        print(f"❌ Error saving recommendation for {user_id}: {e}")
        raise  # Re-lanzar el error para que main.py lo capture

def save_recommendation_v2(supabase, user_id, recommendation):
    """
    Versión alternativa más robusta que maneja diferentes versiones de supabase-py
    """
    today_str = datetime.now().strftime("%Y-%m-%d")

    try:
        # 1. Marcar como "útiles" todas las recomendaciones anteriores con useful = NULL
        print(f"🔄 Updating previous recommendations for {user_id}...")
        
        update_response = supabase.table("recommendations") \
            .update({"useful": True}) \
            .eq("uid", user_id) \
            .is_("useful", None) \
            .execute()

        # Manejo robusto de la respuesta
        updated_count = len(update_response.data) if update_response.data else 0
        print(f"📝 Updated {updated_count} previous recommendations to useful=true")

    except Exception as e:
        print(f"⚠️ Warning updating previous recommendations: {e}")
        # Continuamos con la inserción

    try:
        # 2. Insertar la nueva recomendación
        print(f"💾 Saving new recommendation for {user_id}...")
        
        # Truncar campos si son muy largos para la base de datos
        title = recommendation["title"][:100] if len(recommendation["title"]) > 100 else recommendation["title"]
        description = recommendation["desc"][:300] if len(recommendation["desc"]) > 300 else recommendation["desc"]
        
        # Advertir si se truncó el contenido
        if len(recommendation["title"]) > 100:
            print(f"⚠️ Title was truncated from {len(recommendation['title'])} to 100 characters")
        if len(recommendation["desc"]) > 300:
            print(f"⚠️ Description was truncated from {len(recommendation['desc'])} to 300 characters")
        
        data = {
            "uid": user_id,
            "title": title,
            "description": description,
            "useful": None,
            "date": today_str,
            "type": recommendation["type"]
        }

        insert_response = supabase.table("recommendations").insert(data).execute()

        # Verificar inserción
        if insert_response.data and len(insert_response.data) > 0:
            inserted_id = insert_response.data[0].get('id', 'unknown')
            print(f"✅ Recommendation saved successfully (ID: {inserted_id})")
            return True
        else:
            print(f"⚠️ Unexpected response structure: {insert_response}")
            return False

    except Exception as e:
        print(f"❌ Failed to save recommendation: {e}")
        print(f"Recommendation data: {recommendation}")
        print(f"Title length: {len(recommendation.get('title', ''))}")
        print(f"Description length: {len(recommendation.get('desc', ''))}")
        raise

# Función de utilidad para debugging
def test_supabase_connection(supabase, user_id):
    """
    Función para probar la conexión con Supabase
    """
    try:
        # Probar consulta simple
        response = supabase.table("recommendations").select("*").eq("uid", user_id).limit(1).execute()
        print(f"✅ Supabase connection test successful")
        print(f"Response type: {type(response)}")
        print(f"Has data: {'data' in dir(response)}")
        print(f"Data: {response.data if hasattr(response, 'data') else 'No data attribute'}")
        return True
    except Exception as e:
        print(f"❌ Supabase connection test failed: {e}")
        return False