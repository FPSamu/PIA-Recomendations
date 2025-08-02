import json

def build_prompt(movements, previous_responses):
    # Convertir a JSON strings para evitar problemas con f-strings
    previous_responses_json = json.dumps(previous_responses, indent=2)
    movements_json = json.dumps(movements, indent=2)
    
    # Agregar análisis de contexto para el prompt
    analysis_context = analyze_movements(movements)
    
    prompt = f"""You are a smart financial assistant inside a personal finance app.

IMPORTANT ANALYSIS RULES:
1. READ THE DATA CAREFULLY - Use exact amounts from the data, never make up numbers
2. RECURRENT EXPENSES - Only classify as "recurrent_expenses" if there are 2+ transactions of the same category or similar merchant within the time period
3. SINGLE TRANSACTIONS - A single transaction should be "excessive_expenses" if unusually high, or "savings_opportunities" for general advice
4. AMOUNTS - Always use the EXACT amounts from the transaction data
5. CONTEXT - Consider the transaction amounts in the local currency context (could be pesos, dollars, etc.)

ANALYSIS CONTEXT:
{analysis_context}

You will receive two blocks of information in JSON format:

1. `previousResponses`: Past recommendations already generated for the user
2. `financialMovements`: User's financial transactions from the last 7 days

Your task is to generate ONE new personalized recommendation based on the user's financial activity.

CLASSIFICATION RULES:
- "excessive_expenses": Single large expense or high spending in one category
- "recurrent_expenses": 2+ similar transactions (same category/merchant) showing a pattern
- "savings_opportunities": General advice for optimization or positive financial behavior
- "no_transactions": Only if financialMovements is completely empty - encourage user to start tracking finances

SPECIAL CASE - NO TRANSACTIONS:
If financialMovements is empty, generate a motivational recommendation about the importance of tracking financial transactions regularly. Explain how recording expenses and income helps gain better control over personal finances, identify spending patterns, and make informed financial decisions.

RESPONSE REQUIREMENTS:
- Use EXACT amounts from the data
- Base recommendations on ACTUAL transaction patterns, not assumptions
- Avoid repeating ideas from previousResponses
- Title: Short, attention-grabbing (question or statement), MAX 100 characters
- Description: Clear insight based on real data, MAX 280 characters (keep it concise!)
- Provide actionable advice in brief, clear language

Return ONLY a JSON object with this exact structure:

{{
  "title": "...",
  "desc": "...",
  "type": "..."
}}

---

previousResponses:
{previous_responses_json}

---

financialMovements:
{movements_json}"""
    
    return prompt.strip()

def analyze_movements(movements):
    """
    Analiza los movimientos para dar contexto al modelo
    """
    if not movements:
        return "No financial movements to analyze."
    
    analysis = []
    
    # Contar total de transacciones
    total_transactions = len(movements)
    analysis.append(f"Total transactions: {total_transactions}")
    
    # Separar ingresos y gastos
    expenses = [m for m in movements if m.get('type') == 'expense']
    incomes = [m for m in movements if m.get('type') == 'income']
    
    analysis.append(f"Expenses: {len(expenses)}, Incomes: {len(incomes)}")
    
    if expenses:
        # Análisis de gastos por categoría
        expense_categories = {}
        for expense in expenses:
            category = expense.get('category', 'unknown')
            amount = expense.get('amount', 0)
            if category in expense_categories:
                expense_categories[category]['count'] += 1
                expense_categories[category]['total'] += amount
            else:
                expense_categories[category] = {'count': 1, 'total': amount}
        
        analysis.append("Expense breakdown:")
        for category, data in expense_categories.items():
            analysis.append(f"  - {category}: {data['count']} transactions, total ${data['total']}")
            if data['count'] > 1:
                analysis.append(f"    → RECURRENT PATTERN DETECTED in {category}")
    
    # Transacciones individuales grandes
    large_transactions = [m for m in movements if m.get('amount', 0) > 1000]
    if large_transactions:
        analysis.append(f"Large transactions (>1000): {len(large_transactions)}")
        for tx in large_transactions:
            analysis.append(f"  - {tx.get('title', 'Unknown')}: ${tx.get('amount', 0)} ({tx.get('category', 'unknown')})")
    
    return "\n".join(analysis)

def build_simple_prompt(movements, previous_responses):
    """
    Versión simplificada del prompt para testing
    """
    movements_json = json.dumps(movements, indent=2)
    previous_responses_json = json.dumps(previous_responses, indent=2)
    
    prompt = f"""Analyze these financial transactions and create ONE recommendation.

RULES:
- Use EXACT amounts from the data
- "recurrent_expenses" = 2+ similar transactions only
- "excessive_expenses" = single large expense
- "savings_opportunities" = general advice

DATA:
Movements: {movements_json}
Previous: {previous_responses_json}

Return JSON only:
{{
  "title": "specific title",
  "desc": "based on exact data with real amounts",
  "type": "correct_type"
}}"""
    
    return prompt.strip()

# Función para debug (opcional)
def debug_analysis(movements):
    """
    Función opcional para ver el análisis de movimientos si es necesario debuggear
    """
    print("=== MOVEMENT ANALYSIS ===")
    print(analyze_movements(movements))
    return analyze_movements(movements)