from api.fatsecret_adapter import (
    search_foods,
    get_food_data,
    get_nutrients_by_food_id,
    analyze_food_nutrition,
    compare_foods
)

def call_fatsecret(command: str, args: dict = {}) -> dict:
    """
    Executa uma chamada à API FatSecret com base em um comando e argumentos fornecidos.

    Args:
        command: Nome do comando (ex: 'search_foods', 'get_food_data')
        args: Dicionário com os argumentos necessários

    Returns:
        Resultado da chamada como dicionário
    """
    try:
        if command == "search_foods":
            return search_foods(args.get("query", ""))

        elif command == "get_food_data":
            return get_food_data(int(args.get("food_id")))

        elif command == "get_nutrients_by_food_id":
            return get_nutrients_by_food_id(int(args.get("food_id")))

        elif command == "analyze_food_nutrition":
            return analyze_food_nutrition(int(args.get("food_id")))

        elif command == "compare_foods":
            return compare_foods(int(args.get("food_id_1")), int(args.get("food_id_2")))

        else:
            return {"erro": f"Comando desconhecido: {command}"}
    
    except Exception as e:
        return {"erro": str(e)}
