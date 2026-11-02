import os
from flask import Flask, jsonify, send_from_directory, request

app = Flask(__name__)


@app.route('/')
def index():
    """Servindo o frontend React"""
    return send_from_directory('static', 'index.html')

@app.route('/api/i18n')
def get_translations():
    """Retorna dicionário de traduções por idioma"""
    return jsonify({
        'pt_BR': {
            'title': 'Sistema de Candidatos',
            'subtitle': 'Selecione a hierarquia para ver as informações do candidato',
            'hierarchyTitle': '📊 Hierarquia de Seleção',
            'countryLabel': '🌍 País',
            'partyLabel': '🎭 Partido',
            'positionLabel': '💼 Cargo',
            'candidateLabel': '👤 Candidato',
            'selectCountry': 'Selecione um país...',
            'selectParty': 'Selecione um partido...',
            'selectPosition': 'Selecione uma posição...',
            'selectCandidate': 'Selecione um candidato...',
            'infoTitle': '📋 Informações do Candidato',
            'nameField': 'Nome Completo',
            'ageField': 'Idade',
            'nationalityField': 'Nacionalidade',
            'bioField': 'Biografia',
            'dateField': 'Data da seleção:',
            'emptyState': {
                'title': 'Selecione um país no primeiro dropdown para começar.',
                'subtitle': 'A interface atualiza automaticamente conforme você navega pela hierarquia.'
            }
        },
        'en_US': {
            'title': 'Candidate System',
            'subtitle': 'Select the hierarchy to see candidate information',
            'hierarchyTitle': '📊 Selection Hierarchy',
            'countryLabel': '🌍 Country',
            'partyLabel': '🎭 Party',
            'positionLabel': '💼 Position',
            'candidateLabel': '👤 Candidate',
            'selectCountry': 'Select a country...',
            'selectParty': 'Select a party...',
            'selectPosition': 'Select a position...',
            'selectCandidate': 'Select a candidate...',
            'infoTitle': '📋 Candidate Information',
            'nameField': 'Full Name',
            'ageField': 'Age',
            'nationalityField': 'Nationality',
            'bioField': 'Biography',
            'dateField': 'Selection date:',
            'emptyState': {
                'title': 'Select a country from the first dropdown to begin.',
                'subtitle': 'The interface updates automatically as you navigate through the hierarchy.'
            }
        },
        'es_ES': {
            'title': 'Sistema de Candidatos',
            'subtitle': 'Seleccione la jerarquía para ver la información del candidato',
            'hierarchyTitle': '📊 Jerarquía de Selección',
            'countryLabel': '🌍 País',
            'partyLabel': '🎭 Partido',
            'positionLabel': '💼 Cargo',
            'candidateLabel': '👤 Candidato',
            'selectCountry': 'Seleccione un país...',
            'selectParty': 'Seleccione un partido...',
            'selectPosition': 'Seleccione una posición...',
            'selectCandidate': 'Seleccione un candidato...',
            'infoTitle': '📋 Información del Candidato',
            'nameField': 'Nombre Completo',
            'ageField': 'Edad',
            'nationalityField': 'Nacionalidad',
            'bioField': 'Biografía',
            'dateField': 'Fecha de selección:',
            'emptyState': {
                'title': 'Seleccione un país del primer menú desplegable para comenzar.',
                'subtitle': 'La interfaz se actualiza automáticamente mientras navega por la jerarquía.'
            }
        },
        'es_MX': {
            'title': 'Sistema de Candidatos',
            'subtitle': 'Seleccione el sistema de candidato para ver la información del candidato',
            'hierarchyTitle': '📊 Jerarquía de Selección',
            'countryLabel': '🌍 País',
            'partyLabel': '🎭 Partido',
            'positionLabel': '💼 Cargos',
            'candidateLabel': '👤 Candidato',
            'selectCountry': 'Seleccione un país...',
            'selectParty': 'Seleccione un partido...',
            'selectPosition': 'Seleccione una posición...',
            'selectCandidate': 'Seleccione un candidato...',
            'infoTitle': '📋 Información del Candidato',
            'nameField': 'Nombre Completo',
            'ageField': 'Edad',
            'nationalityField': 'Nacionalidad',
            'bioField': 'Biografía',
            'dateField': 'Fecha de selección:',
            'emptyState': {
                'title': 'Seleccione un país del primer menú desplegable para comenzar.',
                'subtitle': 'La interfaz se actualiza automáticamente mientras navega por la jerarquía.'
            }
        }
    })

# Dicionário de mapeamento País -> Idioma
LOCALE_MAP = {
    1: 'pt_BR',      # Brasil
    2: 'en_US',      # Portugal (usando en_US como placeholder)
    3: 'es_ES',      # Espanha
    4: 'es_MX',      # Argentina (usando es_MX como placeholder)
    5: 'es_MX'       # México
}


# Rota para alternar idioma (não usa catálogo, muda dinamicamente no frontend)
@app.route('/api/carrega_paises')
def carrega_paises():
    """Retorna lista de países com suas localizações e em que idiomas"""
    paises_data = [
        {'id': 1, 'nome': 'Brasil', 'localizacao': 'America/Sao_Paulo'},
        {'id': 2, 'nome': 'Portugal', 'localizacao': 'Europe/Lisbon'},
        {'id': 3, 'nome': 'Espanha', 'localizacao': 'Europe/Madrid'},
        {'id': 4, 'nome': 'Argentina', 'localizacao': 'America/Argentina/Buenos_Aires'},
        {'id': 5, 'nome': 'México', 'localizacao': 'America/Mexico_City'}
    ]
    return jsonify(paises_data)


@app.route('/api/carrega_partidos/<int:pais_id>')
def carrega_partidos(pais_id):
    """Retorna lista de partidos para um país"""
    pais_id_int = int(pais_id)
    locale = LOCALE_MAP.get(pais_id_int, 'pt_BR')
    paises_data = [
        {'id': 1, 'nome': 'Brasil', 'localizacao': 'America/Sao_Paulo'},
        {'id': 2, 'nome': 'Portugal', 'localizacao': 'Europe/Lisbon'},
        {'id': 3, 'nome': 'Espanha', 'localizacao': 'Europe/Madrid'},
        {'id': 4, 'nome': 'Argentina', 'localizacao': 'America/Argentina/Buenos_Aires'},
        {'id': 5, 'nome': 'México', 'localizacao': 'America/Mexico_City'}
    ]
    timezone = paises_data[pais_id_int - 1]['localizacao'] if pais_id_int > 0 else None
    partidos = [
        {'id': 1, 'nome': f'Partido {pais_id}_A'},
        {'id': 2, 'nome': f'Partido {pais_id}_B'},
        {'id': 3, 'nome': f'Partido {pais_id}_C'}
    ]
    # Headers serão tratados no frontend via fetch com Accept-Language
    return jsonify(partidos)


@app.route('/api/carrega_cargos/<int:pais_id>/<int:partido_id>')
def carrega_cargos(pais_id, partido_id):
    """Retorna lista de cargos para um partido"""
    pais_id_int = int(pais_id)
    locale = LOCALE_MAP.get(pais_id_int, 'pt_BR')
    return jsonify([
        {'id': 1, 'nome': f'Cargo {pais_id}_{partido_id}_Presidencia'},
        {'id': 2, 'nome': f'Cargo {pais_id}_{partido_id}_Legislativa'},
        {'id': 3, 'nome': f'Cargo {pais_id}_{partido_id}_Executiva'}
    ])


@app.route('/api/carrega_candidatos/<int:pais_id>/<int:partido_id>/<int:cargo_id>')
def carrega_candidatos(pais_id, partido_id, cargo_id):
    """Retorna lista de candidatos para um cargo"""
    pais_id_int = int(pais_id)
    locale = LOCALE_MAP.get(pais_id_int, 'pt_BR')
    return jsonify([
        {'id': 1, 'nome': f'Candidato {pais_id}_{partido_id}_{cargo_id}_A'},
        {'id': 2, 'nome': f'Candidato {pais_id}_{partido_id}_{cargo_id}_B'},
        {'id': 3, 'nome': f'Candidato {pais_id}_{partido_id}_{cargo_id}_C'}
    ])


@app.route('/api/carrega_info/<int:pais_id>/<int:partido_id>/<int:cargo_id>/<int:candidato_id>')
def carrega_info(pais_id, partido_id, cargo_id, candidato_id):
    """Retorna informações detalhadas do candidato"""
    pais_id_int = int(pais_id)
    locale = LOCALE_MAP.get(pais_id_int, 'pt_BR')
    timezone = request.args.get('timezone') or ('America/Sao_Paulo' if pais_id_int == 1 else 'Europe/Lisbon' if pais_id_int == 2 else 'Europe/Madrid' if pais_id_int == 3 else 'America/Argentina/Buenos_Aires' if pais_id_int == 4 else 'America/Mexico_City')
    return jsonify({
        'pais': f'País {pais_id}',
        'partido': f'Partido {partido_id}',
        'cargo': f'Cargo {cargo_id}',
        'nome': f'Candidato {candidato_id}',
        'idade': f'{20 + (pais_id_int + partido_id + cargo_id + candidato_id) % 50} anos',
        'nacionalidade': f'Nacional do País {pais_id}',
        'biografia': f'Biografia completa do candidato para a posição de {cargo_id} no Partido {partido_id} do País {pais_id}. É um político dedicado e experiente.'
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
    # Desenvolvimento local - usa porta 8000 ou PORT do ambiente
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)
