/**
 * Sistema de Internacionalização (i18n) - Controle dinâmico do idioma
 */

const translations = {
    pt_BR: {
        title: 'Sistema de Candidatos',
        subtitle: 'Selecione a hierarquia para ver as informações do candidato',
        hierarchyTitle: '📊 Hierarquia de Seleção',
        countryLabel: '🌍 País',
        partyLabel: '🎭 Partido',
        positionLabel: '💼 Cargo',
        candidateLabel: '👤 Candidato',
        selectCountry: 'Selecione um país...',
        selectParty: 'Selecione um partido...',
        selectPosition: 'Selecione uma posição...',
        selectCandidate: 'Selecione um candidato...',
        infoTitle: '📋 Informações do Candidato',
        nameField: 'Nome Completo',
        ageField: 'Idade',
        nationalityField: 'Nacionalidade',
        bioField: 'Biografia',
        dateField: 'Data da seleção:',
        emptyState: {
            title: 'Selecione um país no primeiro dropdown para começar.',
            subtitle: 'A interface atualiza automaticamente conforme você navega pela hierarquia.'
        }
    },
    en_US: {
        title: 'Candidate System',
        subtitle: 'Select the hierarchy to see candidate information',
        hierarchyTitle: '📊 Selection Hierarchy',
        countryLabel: '🌍 Country',
        partyLabel: '🎭 Party',
        positionLabel: '💼 Position',
        candidateLabel: '👤 Candidate',
        selectCountry: 'Select a country...',
        selectParty: 'Select a party...',
        selectPosition: 'Select a position...',
        selectCandidate: 'Select a candidate...',
        infoTitle: '📋 Candidate Information',
        nameField: 'Full Name',
        ageField: 'Age',
        nationalityField: 'Nationality',
        bioField: 'Biography',
        dateField: 'Selection date:',
        emptyState: {
            title: 'Select a country from the first dropdown to begin.',
            subtitle: 'The interface updates automatically as you navigate through the hierarchy.'
        }
    },
    es_ES: {
        title: 'Sistema de Candidatos',
        subtitle: 'Seleccione la jerarquía para ver la información del candidato',
        hierarchyTitle: '📊 Jerarquía de Selección',
        countryLabel: '🌍 País',
        partyLabel: '🎭 Partido',
        positionLabel: '💼 Cargo',
        candidateLabel: '👤 Candidato',
        selectCountry: 'Seleccione un país...',
        selectParty: 'Seleccione un partido...',
        selectPosition: 'Seleccione una posición...',
        selectCandidate: 'Seleccione un candidato...',
        infoTitle: '📋 Información del Candidato',
        nameField: 'Nombre Completo',
        ageField: 'Edad',
        nationalityField: 'Nacionalidad',
        bioField: 'Biografía',
        dateField: 'Fecha de selección:',
        emptyState: {
            title: 'Seleccione un país del primer menú desplegable para comenzar.',
            subtitle: 'La interfaz se actualiza automáticamente mientras navega por la jerarquía.'
        }
    },
    es_MX: {
        title: 'Sistema de Candidatos',
        subtitle: 'Seleccione el sistema de candidato para ver la información del candidato',
        hierarchyTitle: '📊 Jerarquía de Selección',
        countryLabel: '🌍 País',
        partyLabel: '🎭 Partido',
        positionLabel: '💼 Cargos',
        candidateLabel: '👤 Candidato',
        selectCountry: 'Seleccione un país...',
        selectParty: 'Seleccione un partido...',
        selectPosition: 'Seleccione una posición...',
        selectCandidate: 'Seleccione un candidato...',
        infoTitle: '📋 Información del Candidato',
        nameField: 'Nombre Completo',
        ageField: 'Edad',
        nationalityField: 'Nacionalidad',
        bioField: 'Biografía',
        dateField: 'Fecha de selección:',
        emptyState: {
            title: 'Seleccione un país del primer menú desplegable para comenzar.',
            subtitle: 'La interfaz se actualiza automáticamente mientras navega por la jerarquía.'
        }
    }
};

const LOCALE_MAP = { 1: 'pt_BR', 2: 'en_US', 3: 'es_ES', 4: 'es_MX', 5: 'es_MX' };

/**
 * Aplica traduções ao idioma selecionado
 */
function applyTranslations(locale) {
    const text = translations[locale] || translations.pt_BR;

    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (key && text[key]) {
            el.textContent = text[key];
        }
    });

    document.documentElement.lang = locale.split('-')[0];
    document.documentElement.classList.remove('lang-en-US', 'lang-es-ES', 'lang-es-MX');

    const prefix = locale.replace('_', '-');
    if (prefix === 'en-us') document.documentElement.classList.add('lang-en-US');
    else if (prefix === 'es-es' || prefix === 'es-mx') document.documentElement.classList.add('lang-es-ES');
}

/**
 * Atualiza labels estáticos baseado no locale atual
 */
function updateStaticLabels() {
    const currentLocale = document.documentElement.lang.replace('-', '_') || 'pt_BR';

    ['countryLabel', 'partyLabel', 'positionLabel', 'candidateLabel',
     'selectCountry', 'selectParty', 'selectPosition', 'selectCandidate'].forEach(key => {
        const el = document.querySelector(`[data-i18n="${key}"]`);
        if (el && translations[currentLocale][key]) {
            el.textContent = translations[currentLocale][key];
        }
    });

    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    const infoTitle = document.querySelector('.info-section h2');

    if (pageTitle) pageTitle.textContent = translations[currentLocale].title;
    if (pageSubtitle) pageSubtitle.textContent = translations[currentLocale].subtitle;
    if (infoTitle) infoTitle.textContent = translations[currentLocale].infoTitle;

    const cards = document.querySelectorAll('.info-card h4');
    if (cards[0]) cards[0].textContent = translations[currentLocale].nameField;
    if (cards[1]) cards[1].textContent = translations[currentLocale].ageField;
    if (cards[2]) cards[2].textContent = translations[currentLocale].nationalityField;
    if (cards[3]) cards[3].textContent = translations[currentLocale].bioField;

    const breadcrumb = document.getElementById('breadcrumb');
    if (breadcrumb) {
        const items = [];
        const paisSelect = document.getElementById('pais-select');
        const partidoSelect = document.getElementById('partido-select');

        if (paisSelect && paisSelect.value) {
            const paisText = paisSelect.options[paisSelect.selectedIndex]?.textContent;
            items.push({ text: paisText, emoji: '🌍' });
        }

        if (partidoSelect && partidoSelect.value) {
            const partidoText = partidoSelect.options[partidoSelect.selectedIndex]?.textContent;
            items.push({ text: partidoText, emoji: '🎭' });
        }

        breadcrumb.innerHTML = items.map(item =>
            `<span class="breadcrumb-item">${item.emoji} ${item.text}</span>`
        ).join('');
    }
}

/**
 * Carrega países - FUNÇÃO PRINCIPAL QUE DEVE RODAR NO INICIALIZAÇÃO
 */
async function loadCountries() {
    try {
        const response = await fetch('/api/carrega_paises');
        if (!response.ok) throw new Error('Erro ao buscar países: ' + response.statusText);

        const paises = await response.json();
        console.log('Países carregados:', paises);

        const select = document.getElementById('pais-select');
        if (select && paises.length > 0) {
            let optionsHTML = '<option value="">Selecione um país...</option>';

            paises.forEach(pais => {
                const locale = LOCALE_MAP[pais.id] || 'pt_BR';
                const formattedLocale = locale.replace('_', '-');

                optionsHTML += `<option value="${pais.id}" data-locale="${formattedLocale}">
                    ${pais.nome}
                </option>`;
            });

            select.innerHTML = optionsHTML;
            console.log('Dropdown de países populado com:', paises.map(p => p.nome).join(', '));
        } else if (select) {
            select.innerHTML = '<option value="">Nenhum país carregado</option>';
        }
    } catch (error) {
        console.error('Erro ao carregar países:', error);
        const select = document.getElementById('pais-select');
        if (select) {
            select.innerHTML = '<option value="">Erro ao carregar países</option>';
        }
    }
}

/**
 * Carrega partidos para o país selecionado
 */
async function loadParties() {
    const paisId = document.getElementById('pais-select').value;

    if (!paisId) return;

    try {
        const response = await fetch(`/api/carrega_partidos/${paisId}`);
        if (!response.ok) throw new Error('Erro ao buscar partidos');

        const partidos = await response.json();

        const select = document.getElementById('partido-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione um partido...</option>';

            partidos.forEach(partido => {
                select.innerHTML += `<option value="${partido.id}">${partido.nome}</option>`;
            });
        }

        console.log('Partidos carregados para país', paisId);
    } catch (error) {
        console.error('Erro ao carregar partidos:', error);
    }
}

/**
 * Carrega cargos para o partido selecionado
 */
async function loadCargos() {
    const paisId = document.getElementById('pais-select').value;
    const partidoId = document.getElementById('partido-select').value;

    if (!paisId || !partidoId) return;

    try {
        const response = await fetch(`/api/carrega_cargos/${paisId}/${partidoId}`);
        if (!response.ok) throw new Error('Erro ao buscar cargos');

        const cargos = await response.json();

        const select = document.getElementById('cargo-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione uma posição...</option>';

            cargos.forEach(cargo => {
                select.innerHTML += `<option value="${cargo.id}">${cargo.nome}</option>`;
            });
        }
    } catch (error) {
        console.error('Erro ao carregar cargos:', error);
    }
}

/**
 * Carrega candidatos para a posição selecionada
 */
async function loadCandidatos() {
    const paisId = document.getElementById('pais-select').value;
    const partidoId = document.getElementById('partido-select').value;
    const cargoId = document.getElementById('cargo-select').value;

    if (!paisId || !partidoId || !cargoId) return;

    try {
        const response = await fetch(`/api/carrega_candidatos/${paisId}/${partidoId}/${cargoId}`);
        if (!response.ok) throw new Error('Erro ao buscar candidatos');

        const candidatos = await response.json();

        const select = document.getElementById('candidato-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione um candidato...</option>';

            candidatos.forEach(candidato => {
                select.innerHTML += `<option value="${candidato.id}">${candidato.nome}</option>`;
            });
        }
    } catch (error) {
        console.error('Erro ao carregar candidatos:', error);
    }
}

/**
 * Carrega informações do candidato selecionado
 */
async function loadInfo() {
    const paisId = document.getElementById('pais-select').value;
    const partidoId = document.getElementById('partido-select').value;
    const cargoId = document.getElementById('cargo-select').value;
    const candidatoId = document.getElementById('candidato-select').value;

    if (!paisId || !partidoId || !cargoId || !candidatoId) return;

    try {
        const timezone = 'America/Sao_Paulo';

        const response = await fetch(`/api/carrega_info/${paisId}/${partidoId}/${cargoId}/${candidatoId}?timezone=${encodeURIComponent(timezone)}`);
        if (!response.ok) throw new Error('Erro ao buscar informações do candidato');

        const info = await response.json();

        // Preenche campos de informação
        const fields = {
            nome: document.getElementById('info-nome'),
            idade: document.getElementById('info-idade'),
            nacionalidade: document.getElementById('info-nacionalidade'),
            biografia: document.getElementById('info-biografia')
        };

        Object.values(fields).forEach(el => {
            if (el) el.textContent = info[el.id] || '';
        });

        // Atualiza breadcrumb
        updateStaticLabels();

        // Mostra seção de informações, esconde estado vazio
        const infoSection = document.querySelector('.info-section');
        const emptyState = document.getElementById('empty-state');

        if (infoSection) infoSection.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';

    } catch (error) {
        console.error('Erro ao carregar informações:', error);
    }
}

/**
 * Event listener para mudança de país - CHAVE PARA MUDANÇA DE IDIOMA E CARREGAR PARTIDOS
 */
const paisSelect = document.getElementById('pais-select');
if (paisSelect) {
    paisSelect.addEventListener('change', function() {
        console.log('Evento change no dropdown de países disparado');

        if (!this.value) {
            console.log('Nenhum país selecionado, resetando níveis inferiores');
            hideLevel(1);
            return;
        }

        // Pega o locale do atributo data-locale da opção selecionada
        const selectedOption = this.options[this.selectedIndex];
        if (!selectedOption || !selectedOption.value) {
            console.log('Opção inválida selecionada');
            hideLevel(1);
            return;
        }

        const newLocale = selectedOption.getAttribute('data-locale') || 'pt_BR';
        const formattedLocale = newLocale.replace('_', '-');

        // 1. MUDA O IDIOMA
        console.log('Mudando idioma para:', formattedLocale);
        applyTranslations(newLocale);

        // 2. ATUALIZA LABELS E UI
        updateStaticLabels();

        // 3. CARREGA PARTIDOS
        loadParties();
    });
}

/**
 * Event listener para mudança de partido
 */
const partidoSelect = document.getElementById('partido-select');
if (partidoSelect) {
    partidoSelect.addEventListener('change', function() {
        console.log('Evento change no dropdown de partidos disparado, valor:', this.value);

        if (this.value) {
            loadCargos();
        } else {
            hideLevel(2);
        }
    });
}

/**
 * Event listener para mudança de cargo
 */
const cargoSelect = document.getElementById('cargo-select');
if (cargoSelect) {
    cargoSelect.addEventListener('change', function() {
        console.log('Evento change no dropdown de cargos disparado, valor:', this.value);

        if (this.value) {
            loadCandidatos();
        } else {
            hideLevel(3);
        }
    });
}

/**
 * Event listener para mudança de candidato
 */
const candidatoSelect = document.getElementById('candidato-select');
if (candidatoSelect) {
    candidatoSelect.addEventListener('change', function() {
        console.log('Evento change no dropdown de candidatos disparado, carregando informações...');
        loadInfo();
    });
}

/**
 * Oculta níveis inferiores
 */
function hideLevel(levelNumber) {
    const levelElement = document.getElementById(`level-${levelNumber}`);
    if (levelElement && levelElement.classList) {
        levelElement.classList.add('level-hidden');
        levelElement.classList.remove('level-active');
    }
}

/**
 * Inicialização ao carregar a página - RODA Imediatamente
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, inicializando aplicação...');

    // Carrega países imediatamente ao carregar a página
    loadCountries();
    console.log('Países solicitados. Aguardando resposta da API...');
});

// Log final para depuração
console.log('i18n.js carregado e pronto!');
console.log('Espera que o DOM esteja carregado, depois carrega países.');
