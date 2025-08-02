from database.client import init_supabase
from database.fetch_data import get_user_data, get_all_user_ids
from llm.prompt_builder import build_prompt
from llm.gemini_api import get_recommendation, test_gemini_connection
from database.upload_data import save_recommendation

def main():
    # Verificar conexión con Gemini antes de procesar usuarios
    print("🔍 Verificando conexión con Gemini...")
    if not test_gemini_connection():
        print("❌ No se puede conectar con Gemini. Verifica tu API key.")
        return
    
    print("🚀 Iniciando procesamiento de usuarios...")
    supabase = init_supabase()

    # 1. Obtener lista de todos los user_ids únicos
    try:
        user_ids = get_all_user_ids(supabase)
        print(f"📊 Encontrados {len(user_ids)} usuarios únicos")
    except Exception as e:
        print(f"❌ Error obteniendo user_ids: {e}")
        return

    processed_count = 0
    error_count = 0
    no_data_count = 0

    for user_id in user_ids:
        try:
            print(f"\n👤 Procesando usuario: {user_id}")

            # 2. Obtener movimientos y recomendaciones del usuario
            movements, past_recommendations = get_user_data(supabase, user_id)

            # Ahora procesamos todos los usuarios, incluso sin movimientos
            has_movements = bool(movements)
            if not movements:
                print(f"📝 Usuario {user_id} sin movimientos recientes — generando recomendación motivacional.")
                movements = []  # Lista vacía para el prompt
                no_data_count += 1
            else:
                print(f"📈 Movimientos encontrados: {len(movements)}")

            print(f"📋 Recomendaciones previas: {len(past_recommendations)}")

            # 3. Construir prompt (ahora funciona con lista vacía también)
            prompt = build_prompt(movements, past_recommendations)

            # 4. Obtener recomendación de Gemini
            recommendation = get_recommendation(prompt)

            if not recommendation:
                print(f"❌ No se pudo generar recomendación para {user_id}")
                error_count += 1
                continue

            print(f"💡 Recomendación generada: {recommendation['title']}")
            print(f"🏷️  Tipo: {recommendation['type']}")

            # 5. Guardar recomendación en Supabase
            save_recommendation(supabase, user_id, recommendation)

            print(f"✅ Recomendación guardada para {user_id}")
            processed_count += 1

        except Exception as e:
            print(f"❌ Error procesando usuario {user_id}: {e}")
            error_count += 1
            continue

    # Resumen final
    with_movements = processed_count - no_data_count
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   Total usuarios: {len(user_ids)}")
    print(f"   Procesados exitosamente: {processed_count}")
    print(f"   - Con movimientos financieros: {with_movements}")
    print(f"   - Sin movimientos (recomendación motivacional): {no_data_count}")
    print(f"   Errores: {error_count}")

if __name__ == "__main__":
    main()