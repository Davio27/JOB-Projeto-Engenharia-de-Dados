let charts = {};
let realtimeInterval = null;
let realtimeData = {
    labels: [],
    usd: [],
    eur: []
};

// Função para alternar tema
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

        Object.values(charts).forEach(chart => {
            if (chart) {
                chart.options.scales.x.ticks.color = '#bdc3c7';
                chart.options.scales.y.ticks.color = '#bdc3c7';
                chart.options.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';
                chart.options.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';
                chart.update();
            }
        });
    } else {
        if (themeIcon) themeIcon.textContent = '🌙';
        if (themeText) themeText.textContent = 'Escuro';
        if (themeIconLogin) themeIconLogin.textContent = '🌙';
        localStorage.setItem('tema', 'light');

        Object.values(charts).forEach(chart => {
            if (chart) {
                chart.options.scales.x.ticks.color = '#7f8c8d';
                chart.options.scales.y.ticks.color = '#7f8c8d';
                chart.options.scales.x.grid.color = 'rgba(0, 0, 0, 0)';
                chart.options.scales.y.grid.color = 'rgba(0, 0, 0, 0.1)';
                chart.update();
            }
        });
    }
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

// Configuração dos gráficos
function inicializarGraficos() {
    fetch('/api/currency-data')
        .then(response => response.json())
        .then(data => {
            inicializarGraficoTempoReal();
            inicializarGraficoUSD(data);
            inicializarGraficoComparativo(data);
            inicializarGraficoVariacao(data);
            inicializarGraficoResumo(data);
        });
}

// Gráfico em tempo real
function inicializarGraficoTempoReal() {
    const ctx = document.getElementById('realtimeChart').getContext('2d');

    const agora = new Date();
    for (let i = 29; i >= 0; i--) {
        const tempo = new Date(agora.getTime() - i * 2000);
        realtimeData.labels.push(tempo.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }));
        realtimeData.usd.push(5.20 + Math.random() * 0.10);
        realtimeData.eur.push(5.60 + Math.random() * 0.15);
    }

    charts.realtime = new Chart(ctx, {
        type: 'line',
        data: {
            labels: realtimeData.labels,
            datasets: [
                {
                    label: 'USD/BRL',
                    data: realtimeData.usd,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#3498db',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                },
                {
                    label: 'EUR/BRL',
                    data: realtimeData.eur,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#e74c3c',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                },
                {
                    label: 'GBP/BRL',
                    data: data.gbp10,
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }
            ]
        },
        options: getLineChartOptions('R$')
    });

    iniciarAtualizacaoTempoReal();
}

// Função para atualizar dados em tempo real
function iniciarAtualizacaoTempoReal() {
    if (realtimeInterval) {
        clearInterval(realtimeInterval);
    }

    realtimeInterval = setInterval(() => {
        const agora = new Date();
        const novoLabel = agora.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        const ultimoUsd = realtimeData.usd[realtimeData.usd.length - 1];
        const ultimoEur = realtimeData.eur[realtimeData.eur.length - 1];

        const novoUsd = ultimoUsd + (Math.random() - 0.5) * 0.02;
        const novoEur = ultimoEur + (Math.random() - 0.5) * 0.025;

        const usdFinal = Math.max(5.10, Math.min(5.40, novoUsd));
        const eurFinal = Math.max(5.50, Math.min(5.80, novoEur));

        realtimeData.labels.push(novoLabel);
        realtimeData.usd.push(usdFinal);
        realtimeData.eur.push(eurFinal);

        if (realtimeData.labels.length > 30) {
            realtimeData.labels.shift();
            realtimeData.usd.shift();
            realtimeData.eur.shift();
        }

        charts.realtime.data.labels = [...realtimeData.labels];
        charts.realtime.data.datasets[0].data = [...realtimeData.usd];
        charts.realtime.data.datasets[1].data = [...realtimeData.eur];
        charts.realtime.update('none');

        atualizarCardsTempoReal(usdFinal, eurFinal, ultimoUsd, ultimoEur);
    }, 2000);
}

// Atualizar cards com dados em tempo real
function atualizarCardsTempoReal(novoUsd, novoEur, ultimoUsd, ultimoEur) {
    const variacaoUsd = novoUsd - ultimoUsd;
    const percentualUsd = (variacaoUsd / ultimoUsd) * 100;

    const variacaoEur = novoEur - ultimoEur;
    const percentualEur = (variacaoEur / ultimoEur) * 100;

    document.getElementById('usd-valor').textContent = `R$ ${novoUsd.toFixed(3)}`;
    const usdVariacao = document.getElementById('usd-variacao');
    const usdSinal = variacaoUsd >= 0 ? '+' : '';
    usdVariacao.textContent = `${usdSinal}${variacaoUsd.toFixed(3)} (${usdSinal}${percentualUsd.toFixed(2)}%)`;
    usdVariacao.className = `variacao ${variacaoUsd >= 0 ? 'positiva' : 'negativa'}`;

    document.getElementById('eur-valor').textContent = `R$ ${novoEur.toFixed(3)}`;
    const eurVariacao = document.getElementById('eur-variacao');
    const eurSinal = variacaoEur >= 0 ? '+' : '';
    eurVariacao.textContent = `${eurSinal}${variacaoEur.toFixed(3)} (${eurSinal}${percentualEur.toFixed(2)}%)`;
    eurVariacao.className = `variacao ${variacaoEur >= 0 ? 'positiva' : 'negativa'}`;

    atualizarUltimaAtualizacao();
}

// Gráfico de linha USD - 30 dias
function inicializarGraficoUSD(data) {
    const ctx = document.getElementById('usdChart').getContext('2d');

    charts.usd = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels30,
            datasets: [{
                label: 'USD/BRL',
                data: data.usd30,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#3498db',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: getLineChartOptions('R$')
    });
}

// Gráfico comparativo USD vs EUR - 30 dias
function inicializarGraficoComparativo(data) {
    const ctx = document.getElementById('comparativoChart').getContext('2d');

    charts.comparativo = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels30,
            datasets: [
                {
                    label: 'USD/BRL',
                    data: data.usd30,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#3498db',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'EUR/BRL',
                    data: data.eur30,
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#27ae60',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: getLineChartOptions('R$')
    });
}

// Gráfico de barras - Variação percentual USD - 15 dias
function inicializarGraficoVariacao(data) {
    const ctx = document.getElementById('variacaoChart').getContext('2d');

    const backgroundColors = data.variacao15.map(value =>
        value >= 0 ? 'rgba(39, 174, 96, 0.8)' : 'rgba(231, 76, 60, 0.8)'
    );
    const borderColors = data.variacao15.map(value =>
        value >= 0 ? '#27ae60' : '#e74c3c'
    );

    charts.variacao = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels15,
            datasets: [{
                label: 'Variação %',
                data: data.variacao15,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: getBarChartOptions('%')
    });
}

// Gráfico resumo - 10 dias
function inicializarGraficoResumo(data) {
    const ctx = document.getElementById('resumoChart').getContext('2d');

    charts.resumo = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels10,
            datasets: [
                {
                    label: 'USD/BRL',
                    data: data.usd10,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#3498db',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'EUR/BRL',
                    data: data.eur10,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#e74c3c',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'BRL (Base)',
                    data: data.brl10,
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: '#f39c12',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderDash: [5, 5]
                }
            ]
        },
        options: getLineChartOptions('R$')
    });
}

// Opções padrão para gráficos de linha
function getLineChartOptions(unit) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        size: 12,
                        weight: '600'
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: '#3498db',
                borderWidth: 1,
                cornerRadius: 10,
                displayColors: true,
                callbacks: {
                    label: function (context) {
                        return context.dataset.label + ': ' + unit + ' ' + context.parsed.y.toFixed(2);
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: 10
                    },
                    color: '#7f8c8d',
                    maxTicksLimit: 10
                }
            },
            y: {
                beginAtZero: false,
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                    font: {
                        size: 10
                    },
                    color: '#7f8c8d',
                    callback: function (value) {
                        return unit + ' ' + value.toFixed(2);
                    }
                }
            }
        },
        interaction: {
            intersect: false,
            mode: 'index'
        }
    };
}

// Opções para gráfico de barras
function getBarChartOptions(unit) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: '#3498db',
                borderWidth: 1,
                cornerRadius: 10,
                displayColors: false,
                callbacks: {
                    label: function (context) {
                        const value = context.parsed.y;
                        const signal = value >= 0 ? '+' : '';
                        return 'Variação: ' + signal + value.toFixed(1) + unit;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: 10
                    },
                    color: '#7f8c8d'
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                    font: {
                        size: 10
                    },
                    color: '#7f8c8d',
                    callback: function (value) {
                        const signal = value >= 0 ? '+' : '';
                        return signal + value.toFixed(1) + unit;
                    }
                }
            }
        }
    };
}

// Atualizar timestamp da última atualização
function atualizarUltimaAtualizacao() {
    const agora = new Date();
    const timestamp = agora.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('ultima-atualizacao').textContent = timestamp;
}

// Inicialização
document.addEventListener('DOMContentLoaded', function () {
    carregarTema();
    if (document.getElementById('dashboard')) {
        inicializarGraficos();
    }
});