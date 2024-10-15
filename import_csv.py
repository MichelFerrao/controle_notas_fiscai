import pandas as pd
import sqlite3

# Conectar ao banco de dados SQLite (ou criar se não existir)
conn = sqlite3.connect('notas_fiscais.db')
cursor = conn.cursor()

# Deletar a tabela antiga (caso já exista com estrutura incorreta)
cursor.execute('DROP TABLE IF EXISTS notas_fiscais')
conn.commit()

# Criar a tabela notas_fiscais com a estrutura correta
cursor.execute('''
CREATE TABLE IF NOT EXISTS notas_fiscais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_emissao TEXT,
    numero_nf TEXT,
    empresa TEXT,
    cliente TEXT,
    produto_servico TEXT,
    valor REAL,
    recebido INTEGER,
    forma_pagamento TEXT,
    data_recebimento TEXT,
    verba TEXT,
    responsavel_entrega TEXT,
    data_entrega TEXT,
    quem_recebeu TEXT
);
''')

conn.commit()

try:
    # Ler o arquivo CSV ignorando a primeira linha
    df = pd.read_csv('dados.csv', encoding='utf-8', sep=';', skiprows=1)

    # Verificar as colunas do CSV
    print("Colunas do CSV:", df.columns)

    # Renomear as colunas para coincidir com as colunas da tabela
    df.columns = [
        'id', 'data_emissao', 'numero_nf', 'empresa', 'cliente', 
        'produto_servico', 'valor', 'recebido', 'forma_pagamento', 
        'data_recebimento', 'verba', 'responsavel_entrega', 
        'data_entrega', 'quem_recebeu'
    ]

    # Remover a coluna 'id' porque ela será autoincrementada pelo banco de dados
    df = df.drop(columns=['id'])

    # Limpar e formatar os dados conforme necessário

    # Remover o "R$" e converter o campo "Valor" para float
    df['valor'] = df['valor'].replace({r'R\$': ''}, regex=True).str.replace('.', '').str.replace(',', '.').astype(float)

    # Inserir os dados no banco de dados SQLite
    df.to_sql('notas_fiscais', conn, if_exists='append', index=False)

    print("Dados importados com sucesso!")

except Exception as e:
    print(f"Erro ao importar dados: {e}")

finally:
    # Fechar a conexão com o banco de dados
    conn.close()

