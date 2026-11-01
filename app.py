from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    """Servindo o frontend React"""
    return send_from_directory('static', 'index.html')


@app.route('/favicon.ico')
def favicon():
    """Servi o ícone da aplicaçao"""
    return send_from_directory('static', 'icon.ico')


@app.route('/static/<path:path>')
def static_files(path):
    """Serve arquivos estáticos do frontend"""
    return send_from_directory('static', path)


# API routes
@app.route('/api/items')
def list_items():
    """Lista todos os itens"""
    return jsonify([
        {'id': 1, 'name': 'Item Um', 'description': 'Descrição do primeiro item'},
        {'id': 2, 'name': 'Item Dois', 'description': 'Descrição do segundo item'},
        {'id': 3, 'name': 'Item Tres', 'description': 'Descrição do terceiro item'}
    ])


@app.route('/api/items/<int:item_id>')
def get_item(item_id):
    """Retorna um item específico pelo ID"""
    return jsonify({
        'id': item_id,
        'name': f'Item {item_id}',
        'description': f'Descrição detalhada do item {item_id}'
    })


@app.route('/api/carrega_paises')
def carrega_paises():
    """Retorna lista de países"""
    return jsonify([
        {'id': 1, 'nome': 'Brasil'},
        {'id': 2, 'nome': 'Portugal'},
        {'id': 3, 'nome': 'Espanha'},
        {'id': 4, 'nome': 'Argentina'},
        {'id': 5, 'nome': 'México'}
    ])


@app.route('/api/carrega_partidos/<int:pais_id>')
def carrega_partidos(pais_id):
    """Retorna lista de partidos para um país"""
    return jsonify([
        {'id': 1, 'nome': f'Partido {pais_id}_A'},
        {'id': 2, 'nome': f'Partido {pais_id}_B'},
        {'id': 3, 'nome': f'Partido {pais_id}_C'}
    ])


@app.route('/api/carrega_cargos/<int:pais_id>/<int:partido_id>')
def carrega_cargos(pais_id, partido_id):
    """Retorna lista de cargos para um partido"""
    return jsonify([
        {'id': 1, 'nome': f'Cargo {pais_id}_{partido_id}_Presidencia'},
        {'id': 2, 'nome': f'Cargo {pais_id}_{partido_id}_Legislativa'},
        {'id': 3, 'nome': f'Cargo {pais_id}_{partido_id}_Executiva'}
    ])


@app.route('/api/carrega_candidatos/<int:pais_id>/<int:partido_id>/<int:cargo_id>')
def carrega_candidatos(pais_id, partido_id, cargo_id):
    """Retorna lista de candidatos para um cargo"""
    return jsonify([
        {'id': 1, 'nome': f'Candidato {pais_id}_{partido_id}_{cargo_id}_A'},
        {'id': 2, 'nome': f'Candidato {pais_id}_{partido_id}_{cargo_id}_B'},
        {'id': 3, 'nome': f'Candidato {pais_id}_{partido_id}_{cargo_id}_C'}
    ])


@app.route('/api/carrega_info/<int:pais_id>/<int:partido_id>/<int:cargo_id>/<int:candidato_id>')
def carrega_info(pais_id, partido_id, cargo_id, candidato_id):
    """Retorna informações detalhadas do candidato"""
    return jsonify({
        'pais': f'País {pais_id}',
        'partido': f'Partido {partido_id}',
        'cargo': f'Cargo {cargo_id}',
        'nome': f'Candidato {candidato_id}',
        'idade': f'{20 + (pais_id + partido_id + cargo_id + candidato_id) % 50} anos',
        'nacionalidade': f'Nacional do País {pais_id}',
        'biografia': f'Biografia completa do candidato para a posição de {cargo_id} no Partido {partido_id} do País {pais_id}. É um político dedicado e experiente.'
    })


@app.route('/api/profile')
def get_profile():
    """Retorna informações do perfil"""
    return jsonify({
        'name': 'Anderson C. Rodrigues',
        'email': 'anderson@example.com'
    })


@app.route('/about')
def about():
    """Página sobre"""
    return jsonify({
        'title': 'Sobre',
        'content': '''
        <html>
            <head><title>Sobre</title></head>
            <body>
                <h1>Página Sobre</h1>
                <p>Esta é uma aplicação Flask integrada com React.</p>
                <p>Você pode acessar outras rotas via API REST.</p>
            </body>
        </html>
        '''
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Servidor funcionando!'})


if __name__ == '__main__':
    app.run()
#    app.run(debug=True)
