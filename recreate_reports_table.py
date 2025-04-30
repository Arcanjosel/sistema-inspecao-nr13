from database.models import DatabaseModels

def main():
    try:
        models = DatabaseModels()
        models.recriar_tabela_relatorios()
        print("Tabela de relatórios recriada com sucesso!")
    except Exception as e:
        print(f"Erro ao recriar tabela: {str(e)}")

if __name__ == "__main__":
    main() 