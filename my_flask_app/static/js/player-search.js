// Player search functionality
document.addEventListener('DOMContentLoaded', function() {
    const playerInput = document.getElementById('compare_player');
    const suggestionsList = document.getElementById('playerSuggestions');
    
    if (!playerInput || !suggestionsList || !window.playersData) {
        return;
    }
    
    const players = window.playersData;

    playerInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        suggestionsList.innerHTML = '';

        if (query.length === 0) {
            suggestionsList.style.display = 'none';
            return;
        }

        // Filter players by matching names
        const matches = players.filter(p => {
            const playerName = p.player_name ? p.player_name.toLowerCase() : '';
            return playerName.includes(query);
        }).slice(0, 10);
        
        if (matches.length > 0) {
            suggestionsList.style.display = 'block';
            
            matches.forEach(player => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = player.player_name;
                
                div.addEventListener('click', function() {
                    playerInput.value = player.player_name;
                    suggestionsList.innerHTML = '';
                    suggestionsList.style.display = 'none';
                });
                
                suggestionsList.appendChild(div);
            });
        } else {
            suggestionsList.style.display = 'none';
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target !== playerInput && e.target.parentElement !== suggestionsList) {
            suggestionsList.style.display = 'none';
        }
    });

    // Show suggestions again when focusing on input
    playerInput.addEventListener('focus', function() {
        if (this.value.length > 0 && suggestionsList.children.length > 0) {
            suggestionsList.style.display = 'block';
        }
    });
});
