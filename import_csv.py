import sqlite3
import pandas as pd

# Conectar ao banco de dados
conn = sqlite3.connect('notas_fiscais.db')
cursor = conn.cursor()

# Criar ou limpar a tabela
cursor.execute('DROP TABLE IF EXISTS notas_fiscais;')
conn.commit()  # Confirma a exclusão da tabela

# Criar a nova tabela
cursor.execute('''
CREATE TABLE notas_fiscais (
    ID INTEGER PRIMARY KEY,
    "Data de emissao" TEXT,
    "Numero NF" TEXT,
    "Empresa" TEXT,
    "Cliente" TEXT,
    "Produto/Servico" TEXT,
    "Valor" REAL,
    "Recebido" INTEGER,
    "Forma de Pagamento" TEXT,
    "Data de Recebimento" TEXT,
    "Verba" TEXT,
    "Responsavel pela Entrega" TEXT,
    "Data de Entrega" TEXT,
    "Quem Recebeu" TEXT
);
''')
conn.commit()  # Confirma a criação da tabela

# Importar os dados do CSV
df = pd.read_csv('dados.csv', sep=';')
df.to_sql('notas_fiscais', conn, if_exists='append', index=False)

# Fechar a conexão
conn.close()
