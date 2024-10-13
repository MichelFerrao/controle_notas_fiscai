import sqlite3

# Cria a conexão com o banco de dados
conn = sqlite3.connect('notas_fiscais.db')
cursor = conn.cursor()

# Criação da tabela de notas fiscais com os novos campos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notas_fiscais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_emissao TEXT NOT NULL,
        empresa TEXT NOT NULL,
        cliente TEXT NOT NULL,
        produto_servico TEXT NOT NULL,
        valor REAL NOT NULL,
        forma_pagamento TEXT,
        data_recebimento TEXT,
        recebido INTEGER,
        verba TEXT,  -- Novo campo
        numero_nf TEXT,  -- Novo campo
        responsavel_entrega TEXT,  -- Novo campo
        data_entrega TEXT,  -- Novo campo
        quem_recebeu TEXT  -- Novo campo
    )
''')

conn.commit()
conn.close()
