/**
 * Sistema de Internacionalização (i18n) - Controle dinâmico do idioma
 */

// Dicionário de tradução para cada idioma
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

// Mapeamento País (id) -> Locale
const LOCALE_MAP = {
    1: 'pt_BR',      // Brasil
    2: 'en_US',      // Portugal
    3: 'es_ES',      // Espanha
    4: 'es_MX',      // Argentina
    5: 'es_MX'       // México
};

// Mapeamento País (id) -> Timezone
const TIMEZONE_MAP = {
    1: 'America/Sao_Paulo',
    2: 'Europe/Lisbon',
    3: 'Europe/Madrid',
    4: 'America/Argentina/Buenos_Aires',
    5: 'America/Mexico_City'
};

/**
 * Aplica as traduções para um idioma específico
 */
function applyTranslations(locale) {
    const text = translations[locale] || translations.pt_BR;

    // Atualiza todos os elementos com atributo data-i18n
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (key && text[key]) {
            el.textContent = text[key];
        }
    });

    // Muda o lang do documento HTML
    document.documentElement.lang = locale.split('-')[0];

    // Remove classes de idioma anteriores
    document.documentElement.classList.remove('lang-en-US', 'lang-es-ES', 'lang-es-MX');

    // Adiciona classe do idioma atual
    if (locale === 'en_US') {
        document.documentElement.classList.add('lang-en-US');
    } else if (locale === 'es_ES' || locale === 'es_MX') {
        document.documentElement.classList.add('lang-es-ES');
    }

    // Retorna o locale formatado com hífen para cabeçalhos HTTP
    return locale.replace('_', '-');
}

/**
 * Atualiza labels estáticos baseado no locale atual
 */
function updateStaticLabels() {
    const currentLocale = document.documentElement.lang.replace('-', '_') || 'pt_BR';

    const labels = ['countryLabel', 'partyLabel', 'positionLabel', 'candidateLabel',
                    'selectCountry', 'selectParty', 'selectPosition', 'selectCandidate',
                    'hierarchyTitle', 'infoTitle', 'nameField', 'ageField',
                    'nationalityField', 'bioField', 'dateField'];

    labels.forEach(key => {
        const el = document.querySelector(`[data-i18n="${key}"]`);
        if (el && translations[currentLocale][key]) {
            el.textContent = translations[currentLocale][key];
        }
    });

    // Atualiza títulos e subtítulos do header
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    if (pageTitle) pageTitle.textContent = translations[currentLocale].title;
    if (pageSubtitle) pageSubtitle.textContent = translations[currentLocale].subtitle;

    // Atualiza títulos de cards de informações
    const infoTitle = document.querySelector('.info-section h2');
    if (infoTitle) infoTitle.textContent = translations[currentLocale].infoTitle;

    const nameField = document.querySelectorAll('.info-card h4').slice(0, 1);
    if (nameField.length > 0) nameField[0].textContent = translations[currentLocale].nameField;

    const ageField = document.querySelectorAll('.info-card h4').slice(1, 2);
    if (ageField.length > 0) ageField[0].textContent = translations[currentLocale].ageField;

    const nationalityField = document.querySelectorAll('.info-card h4').slice(2, 3);
    if (nationalityField.length > 0) nationalityField[0].textContent = translations[currentLocale].nationalityField;

    const bioTitle = document.querySelectorAll('.info-card h4').slice(3, 4);
    if (bioTitle.length > 0) bioTitle[0].textContent = translations[currentLocale].bioField;

    // Atualiza breadcrumb com emojis do idioma atual
    updateBreadcrumbEmojis();
}

/**
 * Atualiza emojis no breadcrumb baseado no locale
 */
function updateBreadcrumbEmojis() {
    const breadcrumbs = document.querySelectorAll('.breadcrumb-item');

    // Pega valores atuais dos selects
    const paisSelect = document.getElementById('pais-select');
    const partidoSelect = document.getElementById('partido-select');
    const cargoSelect = document.getElementById('cargo-select');
    const candidatoSelect = document.getElementById('candidato-select');

    const items = [];

    if (paisSelect && paisSelect.value) {
        items.push({ text: paisSelect.options[paisSelect.selectedIndex]?.textContent, emoji: '🌍' });
    }
    if (partidoSelect && partidoSelect.value) {
        items.push({ text: partidoSelect.options[partidoSelect.selectedIndex]?.textContent, emoji: '🎭' });
    }
    if (cargoSelect && cargoSelect.value) {
        items.push({ text: cargoSelect.options[cargoSelect.selectedIndex]?.textContent, emoji: '💼' });
    }
    if (candidatoSelect && candidatoSelect.value) {
        const nome = candidatoSelect.options[candidatoSelect.selectedIndex]?.textContent;
        items.push({ text: nome, emoji: '👤', short: true });
    }

    // Atualiza o HTML do breadcrumb
    const breadcrumbContainer = document.getElementById('breadcrumb');
    if (breadcrumbContainer) {
        breadcrumbContainer.innerHTML = items.map(item =>
            `<span class="breadcrumb-item">${item.emoji} ${item.text}</span>`
        ).join('');
    }
}

/**
 * Carrega países e configura o primeiro dropdown
 */
async function loadCountries() {
    try {
        const response = await fetch('/api/carrega_paises');
        const paises = await response.json();

        const select = document.getElementById('pais-select');
        if (select) {
            // Adiciona opção inicial
            let optionsHTML = '<option value="">Selecione um país...</option>';

            paises.forEach(pais => {
                const locale = LOCALE_MAP[pais.id] || 'pt_BR';
                const formattedLocale = locale.replace('_', '-');

                optionsHTML += `<option value="${pais.id}" data-locale="${formattedLocale}">
                    ${pais.nome}
                </option>`;
            });

            select.innerHTML = optionsHTML;
        }
    } catch (error) {
        console.error('Erro ao carregar países:', error);
    }
}

/**
 * Carrega partidos para o país selecionado
 */
async function loadParties() {
    const paisId = document.getElementById('pais-select').value;

    if (!paisId) return;

    try {
        // Envia cabeçalho Accept-Language para saber qual idioma usar na resposta se necessário
        const response = await fetch(`/api/carrega_partidos/${paisId}`, {
            headers: {
                'Accept-Language': document.documentElement.lang.replace('-', '_')
            }
        });
        const partidos = await response.json();

        const select = document.getElementById('partido-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione um partido...</option>';

            partidos.forEach(partido => {
                select.innerHTML += `<option value="${partido.id}">${partido.nome}</option>`;
            });
        }

        // Armazena no cache global
        if (!window) window = {};
        window.partidosCache = window.partidosCache || new Map();
        window.partidosCache.set(paisId, partidos);

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
        const response = await fetch(`/api/carrega_cargos/${paisId}/${partidoId}`, {
            headers: {
                'Accept-Language': document.documentElement.lang.replace('-', '_')
            }
        });
        const cargos = await response.json();

        const select = document.getElementById('cargo-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione uma posição...</option>';

            cargos.forEach(cargo => {
                select.innerHTML += `<option value="${cargo.id}">${cargo.nome}</option>`;
            });
        }

        // Cache de cargos
        if (!window.cargosCache) window.cargosCache = new Map();
        const cacheKey = `${paisId}-${partidoId}`;
        window.cargosCache.set(cacheKey, cargos);

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
        const response = await fetch(`/api/carrega_candidatos/${paisId}/${partidoId}/${cargoId}`, {
            headers: {
                'Accept-Language': document.documentElement.lang.replace('-', '_')
            }
        });
        const candidatos = await response.json();

        const select = document.getElementById('candidato-select');
        if (select) {
            select.innerHTML = '<option value="">Selecione um candidato...</option>';

            candidatos.forEach(candidato => {
                select.innerHTML += `<option value="${candidato.id}">${candidato.nome}</option>`;
            });
        }

        // Cache de candidatos
        if (!window.candidatosCache) window.candidatosCache = new Map();
        const cacheKey = `${paisId}-${partidoId}-${cargoId}`;
        window.candidatosCache.set(cacheKey, candidatos);

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
        const timezone = TIMEZONE_MAP[paisId] || 'America/Sao_Paulo';

        const response = await fetch(`/api/carrega_info/${paisId}/${partidoId}/${cargoId}/${candidatoId}?timezone=${encodeURIComponent(timezone)}`, {
            headers: {
                'Accept-Language': document.documentElement.lang.replace('-', '_')
            }
        });
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

        // Atualiza breadcrumb com dados do candidato
        updateBreadcrumbEmojis();

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
        const selectedOption = this.options[this.selectedIndex];

        if (selectedOption.value) {
            // Pega o locale do atributo data-locale da opção selecionada
            const newLocale = selectedOption.getAttribute('data-locale') || 'pt_BR';

            // 1. MUDA O IDIOMA
            const formattedLocale = newLocale.replace('_', '-');
            const displayLocale = applyTranslations(newLocale);

            // 2. ATUALIZA LABELS E UI
            updateStaticLabels();

            console.log(`Idioma alterado para: ${formattedLocale}`);

            // 3. CARREGA PARTIDOS COM O NOVO IDIOMA NO CABEÇALHO
            loadParties();
        } else {
            // Reseta os níveis inferiores
            hideLevel(1);
        }
    });
}

/**
 * Event listener para mudança de partido
 */
const partidoSelect = document.getElementById('partido-select');
if (partidoSelect) {
    partidoSelect.addEventListener('change', function() {
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
    candidatoSelect.addEventListener('change', loadInfo);
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
 * Inicialização ao carregar a página
 */
document.addEventListener('DOMContentLoaded', function() {
    // Carrega países no init
    loadCountries();

    // Garante que o primeiro nível está visível
    const level0 = document.getElementById('level-0');
    if (level0 && level0.classList) {
        level0.classList.add('level-active');
        level0.classList.remove('level-hidden');
    }

    // Event listeners - anexados APÓS DOMContentLoaded quando elementos existem
    const paisSelect = document.getElementById('pais-select');
    if (paisSelect) {
        paisSelect.addEventListener('change', function() {
            console.log('País selecionado:', this.value);  // Debug
            const selectedOption = this.options[this.selectedIndex];

            if (selectedOption && selectedOption.value) {
                // Pega o locale do atributo data-locale da opção selecionada
                const newLocale = selectedOption.getAttribute('data-locale') || 'pt_BR';

                console.log('Idioma:', newLocale);  // Debug

                // 1. MUDA O IDIOMA
                const formattedLocale = newLocale.replace('_', '-');
                applyTranslations(newLocale);

                // 2. ATUALIZA LABELS E UI
                updateStaticLabels();

                console.log(`Idioma alterado para: ${formattedLocale}`);

                // 3. CARREGA PARTIDOS
                loadParties();
            } else {
                console.log('Nenhum país selecionado');
                hideLevel(1);
            }
        });
    }

    const partidoSelect = document.getElementById('partido-select');
    if (partidoSelect) {
        partidoSelect.addEventListener('change', function() {
            if (this.value) {
                loadCargos();
            } else {
                hideLevel(2);
            }
        });
    }

    const cargoSelect = document.getElementById('cargo-select');
    if (cargoSelect) {
        cargoSelect.addEventListener('change', function() {
            if (this.value) {
                loadCandidatos();
            } else {
                hideLevel(3);
            }
        });
    }

    const candidatoSelect = document.getElementById('candidato-select');
    if (candidatoSelect) {
        candidatoSelect.addEventListener('change', loadInfo);
    }
});

// Exportar para uso global (útil para debugging)
if (typeof window !== 'undefined') {
    window.applyTranslations = applyTranslations;
    window.updateStaticLabels = updateStaticLabels;
    window.hideLevel = hideLevel;
}
