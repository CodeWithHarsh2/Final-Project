document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.complete-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const challengeId = this.dataset.id;
            const note = prompt("Add a note about your completion (optional):");
            const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;
            fetch(`/complete_challenge/${challengeId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                },
                body: `note=${encodeURIComponent(note)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const card = document.getElementById(`challenge-${challengeId}`);
                    card.classList.add('completed');
                    form.outerHTML = '<span class="challenge-status">Completed</span>';
                }
            });
        });
    });
});

