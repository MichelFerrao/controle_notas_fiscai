import sqlite3
import csv
import codecs

def create_table():
    conn = sqlite3.connect('notas_fiscais.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notas_fiscais (
        id INTEGER PRIMARY KEY,
        numero_nf TEXT,
        data_criacao TEXT,
        empresa TEXT,
        cliente TEXT,
        produto_servico TEXT,
        tipo TEXT,
        valor REAL,
        recebido TEXT,
        data_recebimento TEXT,
        verba_utilizada TEXT,
        pendente_pagamento TEXT,
        data_entrega TEXT,
        responsavel_entrega TEXT,
        responsavel_recebimento TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print("Tabela criada com sucesso (ou já existia).")

def import_csv():
    create_table()
    conn = sqlite3.connect('notas_fiscais.db')
    cursor = conn.cursor()
    
    try:
        with codecs.open('dados.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                print(f"Importando linha: {row}")
                cursor.execute('''
                INSERT INTO notas_fiscais (numero_nf, data_criacao, empresa, cliente, produto_servico, tipo, valor, recebido, data_recebimento, verba_utilizada, pendente_pagamento, data_entrega, responsavel_entrega, responsavel_recebimento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Nº NF'], row['Data de Emissão'], row['Empresa'], row['Cliente'], row['Produto/Serviço'], 
                    row['Valor'].replace('R$ ', '').replace('.', '').replace(',', '.'),  # Formatar valor corretamente
                    row['Recebido'], row['Data de Recebimento'], row['Verba'], 
                    row['Pendente'], row['Data de Entrega'], row['Responsável pela Entrega'], row['Quem Recebeu']
                ))
            conn.commit()
            print("Importação concluída com sucesso.")
    except Exception as e:
        print(f'Erro ao importar CSV: {e}')
    finally:
        conn.close()

if __name__ == "__main__":
    import_csv()
