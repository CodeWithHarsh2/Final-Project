document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.complete-btn').forEach(btn => {
        btn.onclick = function() {
            const challengeId = this.dataset.challengeId;
            const note = prompt("Add a note about your completion (optional):");
            fetch('/complete_challenge/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `challenge_id=${challengeId}&note=${encodeURIComponent(note)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`challenge-${challengeId}`).classList.add('completed');
                    document.getElementById('xp-bar').style.width = `${data.xp}%`;
                    document.getElementById('level').innerText = `Level: ${data.level}`;
                    if (data.xp === 0) {
                        document.getElementById('level-up').classList.add('show');
                        setTimeout(() => {
                            document.getElementById('level-up').classList.remove('show');
                        }, 2000);
                    }
                }
            });
        };
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
