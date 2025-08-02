from datetime import datetime, timedelta

def get_all_user_ids(supabase):
    # Obtener user_ids únicos desde la tabla transactions
    response = supabase.table("transactions").select("uid").execute()
    records = response.data

    # Extraer valores únicos
    user_ids = list(set(record["uid"] for record in records if record.get("uid")))
    return user_ids

def get_user_data(supabase, user_id):
    # Calcular fecha hace 7 días
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Obtener movimientos financieros del usuario en los últimos 7 días
    transactions_resp = supabase.table("transactions") \
        .select("*") \
        .eq("uid", user_id) \
        .gte("date", seven_days_ago) \
        .execute()
    movements = transactions_resp.data

    # Obtener solo recomendaciones útiles o aún no evaluadas (useful = true o null)
    recommendations_resp = supabase.table("recommendations") \
        .select("*") \
        .eq("uid", user_id) \
        .or_("useful.is.null,useful.eq.true") \
        .execute()
    previous = recommendations_resp.data

    return movements, previous
