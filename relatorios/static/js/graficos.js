document.addEventListener('DOMContentLoaded', function() {
    console.log("Iniciando gráficos..."); // Debug

    // Gráfico de Tendência
    const tendenciaChart = document.getElementById('tendenciaChart');
    if (tendenciaChart) {
        console.log("Dados tendência:", {
            labels: tendenciaChart.dataset.labels,
            abertos: tendenciaChart.dataset.abertos,
            fechados: tendenciaChart.dataset.fechados
        });

        new Chart(tendenciaChart, {
            type: 'line',
            data: {
                labels: JSON.parse(tendenciaChart.dataset.labels || '[]'),
                datasets: [{
                    label: 'Chamados Abertos',
                    data: JSON.parse(tendenciaChart.dataset.abertos || '[]'),
                    borderColor: '#2196F3',
                    fill: false
                }, {
                    label: 'Chamados Fechados',
                    data: JSON.parse(tendenciaChart.dataset.fechados || '[]'),
                    borderColor: '#4CAF50',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Gráfico de Prioridade
    const prioridadeChart = document.getElementById('prioridadeChart');
    if (prioridadeChart) {
        new Chart(prioridadeChart, {
            type: 'pie',
            data: {
                labels: JSON.parse(prioridadeChart.dataset.labels || '[]'),
                datasets: [{
                    data: JSON.parse(prioridadeChart.dataset.data || '[]'),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ]
                }]
            }
        });
    }

    // Gráfico de Operadores
    const operadorChart = document.getElementById('operadorChart');
    if (operadorChart) {
        new Chart(operadorChart, {
            type: 'bar',
            data: {
                labels: JSON.parse(operadorChart.dataset.labels || '[]'),
                datasets: [{
                    label: 'Chamados Atendidos',
                    data: JSON.parse(operadorChart.dataset.data || '[]'),
                    backgroundColor: '#36A2EB'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Gráfico de Tipos
    const tipoChart = document.getElementById('tipoChart');
    if (tipoChart) {
        new Chart(tipoChart, {
            type: 'doughnut',
            data: {
                labels: JSON.parse(tipoChart.dataset.labels || '[]'),
                datasets: [{
                    data: JSON.parse(tipoChart.dataset.data || '[]'),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ]
                }]
            }
        });
    }
});