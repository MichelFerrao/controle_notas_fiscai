import locale
import sqlite3
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Configura o locale para o Brasil (português do Brasil)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para inicializar o banco de dados
def init_db():
    with sqlite3.connect('notas_fiscais.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas_fiscais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_emissao TEXT NOT NULL,
                numero_nf TEXT,
                empresa TEXT NOT NULL,
                cliente TEXT NOT NULL,
                produto_servico TEXT NOT NULL,
                valor REAL NOT NULL,
                recebido INTEGER,
                forma_pagamento TEXT,
                data_recebimento TEXT,
                verba TEXT,
                responsavel_entrega TEXT,
                data_entrega TEXT,
                quem_recebeu TEXT
            )
        ''')
        conn.commit()

# Função para formatar datas
def formatar_data(data):
    try:
        return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return data

@app.route('/')
def index():
    with sqlite3.connect('notas_fiscais.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notas_fiscais")
        notas = cursor.fetchall()

        # Formata o valor e as datas das notas fiscais para o formato brasileiro
        notas_formatadas = []
        for nota in notas:
            nota_formatada = list(nota)
            nota_formatada[1] = formatar_data(nota[1])  # Data de emissão
            nota_formatada[9] = formatar_data(nota[9])  # Data de recebimento
            nota_formatada[12] = formatar_data(nota[12])  # Data de entrega
            
            # Tenta converter o valor para float antes de formatá-lo
            try:
                valor_nota = float(nota[6])
            except ValueError:
                valor_nota = 0.0  # Valor padrão em caso de falha na conversão

            nota_formatada[6] = locale.currency(valor_nota, grouping=True)  # Valor formatado
            notas_formatadas.append(nota_formatada)

    return render_template('index.html', notas=notas_formatadas)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Captura os dados do formulário
        nota = {
            'data_emissao': request.form['data_emissao'],
            'numero_nf': request.form['numero_nf'],
            'empresa': request.form['empresa'],
            'cliente': request.form['cliente'],
            'produto_servico': request.form['produto_servico'],
            'valor': float(request.form['valor']),
            'recebido': request.form.get('recebido') == 'on',  # Converte para booleano
            'forma_pagamento': request.form['forma_pagamento'],
            'data_recebimento': request.form['data_recebimento'] or None,
            'verba': request.form['verba'],
            'responsavel_entrega': request.form['responsavel_entrega'] or None,
            'data_entrega': request.form['data_entrega'] or None,
            'quem_recebeu': request.form['quem_recebeu'] or None,
        }

        with sqlite3.connect('notas_fiscais.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notas_fiscais (
                    data_emissao, numero_nf, empresa, cliente, produto_servico, valor,
                    recebido, forma_pagamento, data_recebimento, verba,
                    responsavel_entrega, data_entrega, quem_recebeu
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nota['data_emissao'], nota['numero_nf'], nota['empresa'], nota['cliente'],
                nota['produto_servico'], nota['valor'], int(nota['recebido']), nota['forma_pagamento'],
                nota['data_recebimento'], nota['verba'], nota['responsavel_entrega'], 
                nota['data_entrega'], nota['quem_recebeu']
            ))
            conn.commit()
        
        return redirect(url_for('index'))  # Redireciona para a página inicial após cadastrar

    return render_template('cadastro.html')

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    with sqlite3.connect('notas_fiscais.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notas_fiscais WHERE id = ?', (id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    with sqlite3.connect('notas_fiscais.db') as conn:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Captura os dados do formulário
            nota = {
                'empresa': request.form['empresa'],
                'cliente': request.form['cliente'],
                'produto_servico': request.form['produto_servico'],
                'valor': float(request.form['valor']),
                'recebido': request.form.get('recebido') == 'on',  # Converte para booleano
                'forma_pagamento': request.form['forma_pagamento'],
                'data_recebimento': request.form.get('data_recebimento') or None,
                'responsavel_entrega': request.form.get('responsavel_entrega'),
                'data_entrega': request.form.get('data_entrega'),
                'quem_recebeu': request.form.get('quem_recebeu')
            }

            # Atualiza os dados no banco de dados
            cursor.execute('''
                UPDATE notas_fiscais
                SET empresa = ?, cliente = ?, produto_servico = ?,
                    valor = ?, recebido = ?, forma_pagamento = ?, data_recebimento = ?,
                    responsavel_entrega = ?, data_entrega = ?,
                    quem_recebeu = ?
                WHERE id = ?
            ''', (
                nota['empresa'], nota['cliente'], nota['produto_servico'], nota['valor'],
                int(nota['recebido']), nota['forma_pagamento'], nota['data_recebimento'],
                nota['responsavel_entrega'], nota['data_entrega'], nota['quem_recebeu'], id
            ))
            conn.commit()
            return redirect(url_for('index'))

        # Se o método for GET, busca os dados da nota fiscal
        cursor.execute('SELECT * FROM notas_fiscais WHERE id = ?', (id,))
        nota = cursor.fetchone()

        # Formata a data para exibir no formulário de edição
        nota_formatada = list(nota)
        nota_formatada[1] = formatar_data(nota[1])  # Data de emissão
        nota_formatada[9] = formatar_data(nota[9])  # Data de recebimento
        nota_formatada[12] = formatar_data(nota[12])  # Data de entrega

    return render_template('edit.html', nota=nota_formatada)

if __name__ == '__main__':
    init_db()  # Inicializa o banco de dados se não existir
    app.run(debug=True)
