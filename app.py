import locale
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

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

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('notas_fiscais.db')
    conn.row_factory = sqlite3.Row  # Isso faz com que os resultados sejam acessíveis por nome de coluna
    return conn

# Função para formatar datas
def formatar_data(data):
    try:
        return datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        return data

# Página inicial que exibe as notas fiscais
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notas_fiscais")
    notas = cursor.fetchall()
    conn.close()

    # Formata o valor e as datas das notas fiscais para o formato brasileiro
    notas_formatadas = []
    for nota in notas:
        nota_formatada = list(nota)
        nota_formatada[1] = formatar_data(nota[1])  # Data de emissão
        nota_formatada[9] = formatar_data(nota[9])  # Data de recebimento
        nota_formatada[12] = formatar_data(nota[12])  # Data de entrega

        # Formata o valor como moeda brasileira
        valor_nota = float(nota[6]) if nota[6] else 0.0
        nota_formatada[6] = locale.currency(valor_nota, grouping=True)  # Valor formatado
        notas_formatadas.append(nota_formatada)

    return render_template('index.html', notas=notas_formatadas)

# Página de cadastro de nova nota fiscal
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
            'recebido': request.form.get('recebido') == 'on',
            'forma_pagamento': request.form['forma_pagamento'],
            'data_recebimento': request.form['data_recebimento'] or None,
            'verba': request.form['verba'],
            'responsavel_entrega': request.form['responsavel_entrega'] or None,
            'data_entrega': request.form['data_entrega'] or None,
            'quem_recebeu': request.form['quem_recebeu'] or None,
        }

        conn = get_db_connection()
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
        conn.close()

        return redirect(url_for('index'))

    return render_template('cadastro.html')

# Página para deletar uma nota fiscal
@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notas_fiscais WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Página para editar uma nota fiscal
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Captura os dados do formulário
        nota = {
            'empresa': request.form['empresa'],
            'cliente': request.form['cliente'],
            'produto_servico': request.form['produto_servico'],
            'valor': float(request.form['valor']),
            'recebido': request.form.get('recebido') == 'on',
            'forma_pagamento': request.form['forma_pagamento'],
            'data_recebimento': request.form.get('data_recebimento') or None,
            'responsavel_entrega': request.form.get('responsavel_entrega'),
            'data_entrega': request.form.get('data_entrega'),
            'quem_recebeu': request.form.get('quem_recebeu')
        }

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
        conn.close()
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM notas_fiscais WHERE id = ?', (id,))
    nota = cursor.fetchone()
    conn.close()

    # Formata a data para exibir no formulário de edição
    nota_formatada = list(nota)
    nota_formatada[1] = formatar_data(nota[1])  # Data de emissão
    nota_formatada[9] = formatar_data(nota[9])  # Data de recebimento
    nota_formatada[12] = formatar_data(nota[12])  # Data de entrega

    return render_template('edit.html', nota=nota_formatada)

# Rota para exibir a página de filtros
@app.route('/filtros')
def filtros():
    return render_template('filtros.html')

# Rota para aplicar filtros e retornar as notas fiscais
@app.route('/api/notas', methods=['GET'])
def get_notas():
    filters = {
        "numero_nf": request.args.get('numero_nf', ''),
        "empresa": request.args.get('empresa', ''),
        "cliente": request.args.get('cliente', ''),
        "produto_servico": request.args.get('produto_servico', ''),
        "valor": request.args.get('valor', ''),
        "recebido": request.args.get('recebido', ''),
        "data_recebimento_inicio": request.args.get('data_recebimento_inicio', ''),
        "data_recebimento_fim": request.args.get('data_recebimento_fim', ''),
    }

    query = "SELECT * FROM notas_fiscais WHERE 1=1"
    params = []

    if filters['numero_nf']:
        query += " AND numero_nf LIKE ?"
        params.append(f"%{filters['numero_nf']}%")
    if filters['empresa']:
        query += " AND empresa LIKE ?"
        params.append(f"%{filters['empresa']}%")
    if filters['cliente']:
        query += " AND cliente LIKE ?"
        params.append(f"%{filters['cliente']}%")
    if filters['produto_servico']:
        query += " AND produto_servico LIKE ?"
        params.append(f"%{filters['produto_servico']}%")
    if filters['valor']:
        query += " AND valor = ?"
        params.append(filters['valor'])
    if filters['recebido']:
        query += " AND recebido = ?"
        params.append(1 if filters['recebido'] == 'on' else 0)
    if filters['data_recebimento_inicio']:
        query += " AND data_recebimento >= ?"
        params.append(filters['data_recebimento_inicio'])
    if filters['data_recebimento_fim']:
        query += " AND data_recebimento <= ?"
        params.append(filters['data_recebimento_fim'])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    notas = cursor.fetchall()
    conn.close()

    # Formata as notas para a resposta JSON
    notas_formatadas = []
    for nota in notas:
        nota_formatada = list(nota)
        nota_formatada[1] = formatar_data(nota[1])  # Data de emissão
        nota_formatada[9] = formatar_data(nota[9])  # Data de recebimento
        nota_formatada[12] = formatar_data(nota[12])  # Data de entrega

        valor_nota = float(nota[6]) if nota[6] else 0.0
        nota_formatada[6] = locale.currency(valor_nota, grouping=True)  # Valor formatado
        notas_formatadas.append(nota_formatada)

    return jsonify(notas_formatadas)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

@app.route('/resultados', methods=['POST'])
def resultados():
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']
    empresa = request.form['empresa']
    cliente = request.form['cliente']
    
    # Aqui você processaria os filtros e retornaria os resultados
    return f"Filtros aplicados: {data_inicio} a {data_fim}, Empresa: {empresa}, Cliente: {cliente}"

from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')  # Ajuste o caminho do banco de dados conforme necessário
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    notas = conn.execute('SELECT * FROM notas_fiscais').fetchall()
    conn.close()
    return render_template('index.html', notas=notas)

@app.route('/filtros', methods=['GET', 'POST'])
def filtros():
    if request.method == 'POST':
        # Obtendo os parâmetros de filtro do formulário
        empresa = request.form.get('empresa')
        cliente = request.form.get('cliente')
        recebido = request.form.get('recebido')

        # Montando a consulta SQL baseada nos filtros
        query = 'SELECT * FROM notas_fiscais WHERE 1=1'
        params = []

        if empresa:
            query += ' AND empresa LIKE ?'
            params.append(f'%{empresa}%')
        
        if cliente:
            query += ' AND cliente LIKE ?'
            params.append(f'%{cliente}%')
        
        if recebido is not None:  # recebido pode ser "sim" ou "não"
            if recebido == 'sim':
                query += ' AND recebido = 1'
            else:
                query += ' AND recebido = 0'

        conn = get_db_connection()
        notas = conn.execute(query, params).fetchall()
        conn.close()
        
        return render_template('filtros.html', notas=notas)
    
    return render_template('filtros.html', notas=[])

if __name__ == '__main__':
    app.run(debug=True)


