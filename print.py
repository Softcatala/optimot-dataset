import json

def read_jsonl_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            entry = json.loads(line)
            print("Fitxa:", entry.get("Fitxa", ""))
            print("Darrera versió:", entry.get("Darrera versió", ""))
            print("Títol:", entry.get("Títol", ""))
            print("Pregunta:", entry.get("Pregunta", ""))
#           print("Opcions:", entry.get("Opcions", []))
            print("Resposta:", entry.get("Resposta", ""))
            print("-" * 80)

if __name__ == "__main__":
    read_jsonl_file("optimot.jsonl")
