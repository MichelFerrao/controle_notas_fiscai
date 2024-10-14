import pandas as pd
import sqlite3

# Conectar ao banco de dados SQLite (ou criar se não existir)
conn = sqlite3.connect('notas_fiscais.db')
cursor = conn.cursor()

# Criar a tabela notas_fiscais (caso ainda não exista)
# Ajuste os tipos de dados conforme necessário para suas colunas
cursor.execute('''
CREATE TABLE IF NOT EXISTS notas_fiscais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    empresa TEXT,
    cliente TEXT,
    produto TEXT,
    tipo TEXT,
    valor REAL,
    forma_pagamento TEXT,
    numero_nf TEXT,
    data_recebimento TEXT,
    recebido TEXT
)
''')

conn.commit()

try:
    # Ler o arquivo CSV usando pandas
    df = pd.read_csv('dados.csv')
    
    # Verificar se as colunas do CSV correspondem às colunas da tabela
    print("Colunas do CSV:", df.columns)

    # Inserir os dados no banco de dados SQLite
    df.to_sql('notas_fiscais', conn, if_exists='append', index=False)
    
    print("Dados importados com sucesso!")

except Exception as e:
    print("Erro ao importar dados:", e)

finally:
    # Fechar a conexão com o banco de dados
    conn.close()
