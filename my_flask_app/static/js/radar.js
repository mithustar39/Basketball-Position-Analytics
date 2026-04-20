let myRadarChart;

document.addEventListener('DOMContentLoaded', function() {
    // Set up close button handler
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.onclick = () => {
            document.getElementById('chartModal').style.display = "none";
        };
    }

    // Set up modal close on outside click
    window.onclick = function(event) {
        const modal = document.getElementById('chartModal');
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Set up view stats buttons
    document.querySelectorAll('.view-stats').forEach(button => {
        button.addEventListener('click', function() {

            const name = this.getAttribute('data-name');
            
            const stats = [
                parseFloat(this.getAttribute('data-fgpct')) * 10, 
                parseFloat(this.getAttribute('data-tp_pct')) * 10,
                parseFloat(this.getAttribute('data-stl')),
                parseFloat(this.getAttribute('data-blk')),
                parseFloat(this.getAttribute('data-tov')),
                parseFloat(this.getAttribute('data-pf')),
                parseFloat(this.getAttribute('data-pts')) / 4,
                parseFloat(this.getAttribute('data-ast')),
                parseFloat(this.getAttribute('data-trb'))
            ];

            document.getElementById('modalPlayerName').innerText = name;
            document.getElementById('chartModal').style.display = "flex";

            const ctx = document.getElementById('radarChart').getContext('2d');
            
            if (myRadarChart) { myRadarChart.destroy(); }

            myRadarChart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['FG% (1-10)', '3P% (1-10)', 'Steals', 'Blocks', 'TOV', 'Fouls', 'PPG Rating (1-10)', 'Assists', 'Rebounds'],
                    datasets: [{
                        label: name,
                        data: stats,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)', 
                        borderColor: 'rgb(255, 99, 132)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgb(255, 99, 132)',
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    layout: { padding: 40 },
                    scales: {
                        r: {
                            beginAtZero: true,
                            suggestedMax: 10, 
                            ticks: { display: false },
                            pointLabels: {
                                font: { size: 12, weight: 'bold' },
                                padding: 15
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        });
    });
});