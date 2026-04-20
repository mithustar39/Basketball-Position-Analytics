let comparisonRadarChart;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the comparison radar chart if the canvas exists
    const canvas = document.getElementById('comparisonRadarChart');
    if (canvas) {
        createComparisonRadarChart();
    }
});

function createComparisonRadarChart() {
    // Get data from data attributes on the canvas
    const canvas = document.getElementById('comparisonRadarChart');
    const userStatsStr = canvas.getAttribute('data-user-stats');
    const playerStatsStr = canvas.getAttribute('data-player-stats');
    
    const userStats = JSON.parse(userStatsStr);
    const playerStats = JSON.parse(playerStatsStr);
    
    // Calculate normalized stats for radar chart
    // Using the same scale conversions as the single player radar
    const userRadarStats = [
        userStats.fg_pct * 10,           // FG% (1-10)
        userStats.three_p_pct * 10,      // 3P% (1-10)
        userStats.stl,                   // Steals
        userStats.blk,                   // Blocks
        userStats.tov,                   // TOV
        userStats.pf,                    // Fouls
        userStats.pts / 4,               // PPG Rating (1-10)
        userStats.ast,                   // Assists
        userStats.trb                    // Rebounds
    ];
    
    const playerRadarStats = [
        playerStats.fg_pct * 10,         // FG% (1-10)
        playerStats.three_p_pct * 10,    // 3P% (1-10)
        playerStats.stl,                 // Steals
        playerStats.blk,                 // Blocks
        playerStats.tov,                 // TOV
        playerStats.pf,                  // Fouls
        playerStats.pts / 4,             // PPG Rating (1-10)
        playerStats.ast,                 // Assists
        playerStats.trb                  // Rebounds
    ];
    
    const ctx = canvas.getContext('2d');
    
    if (comparisonRadarChart) { 
        comparisonRadarChart.destroy(); 
    }

    comparisonRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['FG% (1-10)', '3P% (1-10)', 'Steals', 'Blocks', 'TOV', 'Fouls', 'PPG Rating (1-10)', 'Assists', 'Rebounds'],
            datasets: [
                {
                    label: 'Your Stats',
                    data: userRadarStats,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',      // Blue
                    borderColor: 'rgb(54, 162, 235)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                },
                {
                    label: playerStats.player_name || 'Comparison Player',
                    data: playerRadarStats,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',       // Red
                    borderColor: 'rgb(255, 99, 132)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgb(255, 99, 132)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            layout: { 
                padding: 40 
            },
            scales: {
                r: {
                    beginAtZero: true,
                    suggestedMax: 10, 
                    ticks: { 
                        display: true,
                        font: { size: 11 }
                    },
                    pointLabels: {
                        font: { size: 12, weight: 'bold' },
                        padding: 15
                    }
                }
            },
            plugins: {
                legend: { 
                    display: true,
                    position: 'top',
                    labels: {
                        font: { size: 14, weight: 'bold' },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                title: {
                    display: true,
                    text: 'Player Stats Comparison Radar Chart',
                    font: { size: 16, weight: 'bold' },
                    padding: 20
                }
            }
        }
    });
}
