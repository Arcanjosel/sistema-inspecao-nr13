import pyodbc
import os
from dotenv import load_dotenv

def check_database():
    try:
        load_dotenv()
        
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_NAME')
        
        conn_str = (
            f"DRIVER={{SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
        
        print(f"Tentando conectar ao banco de dados: {server}/{database}")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Verifica tabelas
        cursor.execute("SELECT name FROM sys.tables")
        tables = cursor.fetchall()
        print("\nTabelas encontradas:")
        for table in tables:
            print(f"- {table[0]}")
            
        # Verifica usuários
        cursor.execute("SELECT id, nome, email, tipo_acesso FROM usuarios")
        users = cursor.fetchall()
        print("\nUsuários encontrados:")
        for user in users:
            print(f"- ID: {user[0]}, Nome: {user[1]}, Email: {user[2]}, Tipo: {user[3]}")
            
        cursor.close()
        conn.close()
        print("\nConexão com o banco de dados estabelecida com sucesso!")
        
    except Exception as e:
        print(f"\nErro ao conectar ao banco de dados: {str(e)}")

if __name__ == "__main__":
    check_database() 