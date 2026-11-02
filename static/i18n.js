console.log('=== i18n.js carregado ===');

// Dados simples de tradução
const trad = {
    'pt_BR': { title: 'Sistema', countryLabel: '🌍 País', partyLabel: '🎭 Partido' },
    'en_US': { title: 'System', countryLabel: '🌍 Country', partyLabel: '🎭 Party' },
    'es_ES': { title: 'Sistema', countryLabel: '🌍 País', partyLabel: '🎭 Partido' }
};

// Dados de países (serão carregados da API)
var paises = [];

// Carrega países da API
async function carregarPaises() {
    console.log('Carregando países...');
    try {
        const resp = await fetch('/api/carrega_paises');
        if (!resp.ok) throw new Error(resp.statusText);
        paises = await resp.json();
        console.log('Países:', paises);

        // Preenche dropdown de países
        var select = document.getElementById('pais-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione um país...</option>';
            paises.forEach(function(pais) {
                var locale = pais.id === 1 ? 'pt-BR' : pais.id === 2 ? 'en-US' : 'es-ES';
                var opt = document.createElement('option');
                opt.value = pais.id;
                opt.textContent = pais.nome;
                opt.setAttribute('data-locale', locale);
                select.appendChild(opt);
            });

            // Adiciona evento de mudança
            select.onchange = function() {
                console.log('País selecionado:', this.value);
                if (!this.value) return;

                var paisId = parseInt(this.value);
                var locale = this.options[this.selectedIndex].getAttribute('data-locale');

                // 1. Muda idioma
                document.documentElement.lang = locale.split('-')[0];
                console.log('Idioma:', locale, '→', locale.split('-')[0]);

                // 2. Atualiza labels
                updateLabels();

                // 3. Carrega partidos
                carregarPartidos(paisId);
            };
        }
    } catch (e) {
        console.error('Erro ao carregar países:', e);
    }
}

// Carrega partidos
async function carregarPartidos(id) {
    console.log('Carregando partidos para país', id);
    try {
        var resp = await fetch('/api/carrega_partidos/' + id);
        if (!resp.ok) throw new Error(resp.statusText);
        var partidos = await resp.json();

        var select = document.getElementById('partido-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione um partido...</option>';
            partidos.forEach(function(p) {
                var opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.nome;
                select.appendChild(opt);
            });

            // Quando seleciona partido, carrega cargos
            select.onchange = function() {
                if (!this.value) return hideNivel(2);
                console.log('Partido:', this.value);
                carregarCargos(id, this.value);
            };
        }
    } catch (e) {
        console.error('Erro ao carregar partidos:', e);
    }
}

// Carrega cargos
async function carregarCargos(paisId, partidoId) {
    var resp = await fetch('/api/carrega_cargos/' + paisId + '/' + partidoId);
    if (!resp.ok) throw new Error(resp.statusText);
    var cargos = await resp.json();

    var select = document.getElementById('cargo-select');
    if (select) {
        select.innerHTML = '<option value="">Selecione uma posição...</option>';
        cargos.forEach(function(c) {
            var opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.nome;
            select.appendChild(opt);
        });

        select.onchange = function() {
            if (!this.value) return hideNivel(3);
            console.log('Cargos carregados:', this.value);
            carregarCandidatos(paisId, partidoId, this.value);
        };
    }
}

// Carrega candidatos
async function carregarCandidatos(paisId, partidoId, cargoId) {
    var resp = await fetch('/api/carrega_candidatos/' + paisId + '/' + partidoId + '/' + cargoId);
    if (!resp.ok) throw new Error(resp.statusText);
    var candidatos = await resp.json();

    var select = document.getElementById('candidato-select');
    if (select) {
        select.innerHTML = '<option value="">Selecione um candidato...</option>';
        candidatos.forEach(function(c) {
            var opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.nome;
            select.appendChild(opt);
        });

        select.onchange = function() {
            console.log('Candidato carregando info...');
            carregarInfo(this.value, paisId, partidoId, cargoId);
        };
    }
}

// Carrega informações do candidato
async function carregarInfo(id, paisId, partidoId, cargoId) {
    var resp = await fetch('/api/carrega_info/' + paisId + '/' + partidoId + '/' + cargoId + '/' + id);
    if (!resp.ok) throw new Error(resp.statusText);
    var info = await resp.json();

    console.log('Info do candidato:', info);

    // Mostra informações
    document.getElementById('info-nome').textContent = info.nome;
    document.getElementById('info-idade').textContent = info.idade;
    document.getElementById('info-nacionalidade').textContent = info.nacionalidade;
    document.getElementById('info-biografia').textContent = info.biografia;

    // Esconde estado vazio, mostra informações
    document.getElementById('empty-state').style.display = 'none';
    document.querySelector('.info-section').style.display = 'block';
}

// Atualiza labels baseado no idioma atual
function updateLabels() {
    var lang = document.documentElement.lang;
    console.log('Atualizando UI para:', lang);

    // Tenta encontrar o título da página (pode ter vários elementos com id="page-title")
    var titles = document.querySelectorAll('[data-i18n="title"]');
    if (titles.length > 0) {
        titles.forEach(function(el) {
            el.textContent = trad[lang] ? trad[lang].title : 'Sistema';
        });
    } else {
        // Fallback: atualiza todos os elementos data-i18n
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var key = el.getAttribute('data-i18n');
            if (key && trad[lang]) {
                el.textContent = trad[lang][key] || el.textContent;
            }
        });
    }

    console.log('Títulos atualizados:', titles.length);
}

// Oculta nível inferior
function hideNivel(nivel) {
    var el = document.getElementById('level-' + nivel);
    if (el && el.classList) {
        el.classList.add('level-hidden');
        el.classList.remove('level-active');
    }
}

// Inicializa
console.log('Iniciando i18n...');
carregarPaises();
