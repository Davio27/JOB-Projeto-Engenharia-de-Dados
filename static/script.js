let charts = {};
let realtimeData = { labels: [], usd: [], eur: [] };
let realtimeInterval = null;

// Alternar tema
function alternarTema() {
    const body = document.body;
    const themeIcon = document.querySelector('.theme-icon');
    const themeText = document.querySelector('.theme-text');
    const themeIconLogin = document.querySelector('.theme-icon-login');

    body.classList.toggle('dark-theme');

    if (body.classList.contains('dark-theme')) {
        if (themeIcon) themeIcon.textContent = '☀️';
        if (themeText) themeText.textContent = 'Claro';
        if (themeIconLogin) themeIconLogin.textContent = '☀️';
        localStorage.setItem('tema', 'dark');
    } else {
        if (themeIcon) themeIcon.textContent = '🌙';
        if (themeText) themeText.textContent = 'Escuro';
        if (themeIconLogin) themeIconLogin.textContent = '🌙';
        localStorage.setItem('tema', 'light');
    }

    Object.values(charts).forEach(chart => chart && chart.update());
}

// Carregar tema salvo
function carregarTema() {
    const temaSalvo = localStorage.getItem('tema');
    if (temaSalvo === 'dark') {
        document.body.classList.add('dark-theme');
        const themeIcon = document.querySelector('.theme-icon');
        const themeText = document.querySelector('.theme-text');
        const themeIconLogin = document.querySelector('.theme-icon-login');
        if (themeIcon) themeIcon.textContent = '☀️';
        if (themeText) themeText.textContent = 'Claro';
        if (themeIconLogin) themeIconLogin.textContent = '☀️';
    }
}

// Atualizar timestamp da última atualização
function atualizarUltimaAtualizacao() {
    const agora = new Date();
    const timestamp = agora.toLocaleString('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
    const elem = document.getElementById('ultima-atualizacao');
    if (elem) elem.textContent = timestamp;
}

// Dados mock para fallback
function gerarDadosMock() {
    const labels30 = Array.from({ length: 30 }, (_, i) => `Dia ${i+1}`);
    const usd30 = Array.from({ length: 30 }, () => +(5 + Math.random()*0.5).toFixed(3));
    const eur30 = Array.from({ length: 30 }, () => +(5.5 + Math.random()*0.3).toFixed(3));
    const variation15 = Array.from({ length: 15 }, () => +((Math.random()-0.5)*2).toFixed(2));
    const labels15 = Array.from({ length: 15 }, (_, i) => `Dia ${i+1}`);
    const labels10 = Array.from({ length: 10 }, (_, i) => `Dia ${i+1}`);
    const usd10 = Array.from({ length: 10 }, () => +(5 + Math.random()*0.5).toFixed(3));
    const eur10 = Array.from({ length: 10 }, () => +(5.5 + Math.random()*0.3).toFixed(3));
    const brl10 = Array.from({ length: 10 }, () => 1.0);
    const gbp10 = Array.from({ length: 10 }, () => +(6 + Math.random()*0.4).toFixed(3));
    const gbp30 = Array.from({ length: 30 }, () => +(6 + Math.random()*0.4).toFixed(3));

    return { labels30, usd30, eur30, labels15, variation15, labels10, usd10, eur10, brl10, gbp10, gbp30 };
}

// Inicializar gráficos
function inicializarGraficos() {
    fetch('/api/currency-data')
        .then(res => res.json())
        .then(data => renderizarGraficos(data))
        .catch(err => {
            console.warn('Falha ao carregar API, usando dados mock.', err);
            renderizarGraficos(gerarDadosMock());
        });
}

// Renderiza gráficos
function renderizarGraficos(data) {
    // USD 30 dias
    const ctxUsd = document.getElementById('usdChart').getContext('2d');
    charts.usd = new Chart(ctxUsd, {
        type: 'line',
        data: { labels: data.labels30, datasets: [{ label: 'USD/BRL', data: data.usd30, borderColor: '#3498db', fill: false }] },
        options: getLineChartOptions('R$')
    });

    // Comparativo USD vs EUR 30 dias
    const ctxComp = document.getElementById('comparativoChart').getContext('2d');
    charts.comparativo = new Chart(ctxComp, {
        type: 'line',
        data: {
            labels: data.labels30,
            datasets: [
                { label: 'USD/BRL', data: data.usd30, borderColor: '#3498db', fill: false },
                { label: 'EUR/BRL', data: data.eur30, borderColor: '#e74c3c', fill: false }
            ]
        },
        options: getLineChartOptions('R$')
    });

    // Variação % 15 dias
    const ctxVar = document.getElementById('variacaoChart').getContext('2d');
    const backgroundColors = data.variation15.map(v => v >= 0 ? 'rgba(39,174,96,0.8)' : 'rgba(231,76,60,0.8)');
    const borderColors = data.variation15.map(v => v >= 0 ? '#27ae60' : '#e74c3c');

    charts.variacao = new Chart(ctxVar, {
        type: 'bar',
        data: {
            labels: data.labels15,
            datasets: [{
                label: 'Variação %',
                data: data.variation15,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: getBarChartOptions('%')
    });

    // Resumo 10 dias
    const ctxResumo = document.getElementById('resumoChart').getContext('2d');
    charts.resumo = new Chart(ctxResumo, {
        type: 'line',
        data: {
            labels: data.labels10,
            datasets: [
                { label: 'USD/BRL', data: data.usd10, borderColor: '#3498db', fill: false },
                { label: 'EUR/BRL', data: data.eur10, borderColor: '#e74c3c', fill: false },
                { label: 'BRL (Base)', data: data.brl10, borderColor: '#f39c12', fill: false }
            ]
        },
        options: getLineChartOptions('R$')
    });

    // Gráfico tempo real
    inicializarGraficoTempoReal();
}

// Tempo real
function inicializarGraficoTempoReal() {
    fetch('/api/realtime-data-short')
        .then(res => res.json())
        .then(data => {
            realtimeData.labels = data.labels;
            realtimeData.usd = data.usd;
            realtimeData.eur = data.eur;

            const ctx = document.getElementById('realtimeChart').getContext('2d');
            charts.realtime = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: realtimeData.labels,
                    datasets: [
                        { label: 'USD/BRL', data: realtimeData.usd, borderColor: '#3498db', fill: false, pointRadius: 0, tension: 0.4 },
                        { label: 'EUR/BRL', data: realtimeData.eur, borderColor: '#e74c3c', fill: false, pointRadius: 0, tension: 0.4 }
                    ]
                },
                options: getLineChartOptions('R$')
            });

            iniciarAtualizacaoTempoReal();
        });
}

// Atualização do tempo real a cada minuto
function iniciarAtualizacaoTempoReal() {
    if (realtimeInterval) clearInterval(realtimeInterval);
    realtimeInterval = setInterval(() => {
        fetch('/api/realtime-data')
            .then(res => res.json())
            .then(data => {
                realtimeData.labels = data.labels;
                realtimeData.usd = data.usd;
                realtimeData.eur = data.eur;

                charts.realtime.data.labels = [...realtimeData.labels];
                charts.realtime.data.datasets[0].data = [...realtimeData.usd];
                charts.realtime.data.datasets[1].data = [...realtimeData.eur];
                charts.realtime.update('none');

                // Atualiza cards
                const novoUsd = realtimeData.usd.at(-1);
                const novoEur = realtimeData.eur.at(-1);
                const ultimoUsd = realtimeData.usd.at(-2) || novoUsd;
                const ultimoEur = realtimeData.eur.at(-2) || novoEur;
                atualizarCardsTempoReal(novoUsd, novoEur, ultimoUsd, ultimoEur);
            });
    }, 60000);
}

// Atualiza cards USD/EUR
function atualizarCardsTempoReal(novoUsd, novoEur, ultimoUsd, ultimoEur) {
    const variacaoUsd = novoUsd - ultimoUsd;
    const percentualUsd = (variacaoUsd / ultimoUsd) * 100;
    const variacaoEur = novoEur - ultimoEur;
    const percentualEur = (variacaoEur / ultimoEur) * 100;

    document.getElementById('usd-valor').textContent = `R$ ${novoUsd.toFixed(3)}`;
    const usdVar = document.getElementById('usd-variacao');
    usdVar.textContent = `${variacaoUsd >= 0 ? '+' : ''}${variacaoUsd.toFixed(3)} (${variacaoUsd >= 0 ? '+' : ''}${percentualUsd.toFixed(2)}%)`;
    usdVar.className = `variacao ${variacaoUsd >= 0 ? 'positiva' : 'negativa'}`;

    document.getElementById('eur-valor').textContent = `R$ ${novoEur.toFixed(3)}`;
    const eurVar = document.getElementById('eur-variacao');
    eurVar.textContent = `${variacaoEur >= 0 ? '+' : ''}${variacaoEur.toFixed(3)} (${variacaoEur >= 0 ? '+' : ''}${percentualEur.toFixed(2)}%)`;
    eurVar.className = `variacao ${variacaoEur >= 0 ? 'positiva' : 'negativa'}`;

    atualizarUltimaAtualizacao();
}

// Chart.js options
function getLineChartOptions(unit) {
    return { responsive: true, maintainAspectRatio: false };
}
function getBarChartOptions(unit) {
    return { responsive: true, maintainAspectRatio: false };
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarTema();
    if (document.getElementById('dashboard')) inicializarGraficos();
});
