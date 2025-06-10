document.addEventListener('DOMContentLoaded', function () {
    const generateBtn = document.getElementById('generate-avatar-btn');
    const avatarPreview = document.getElementById('avatar-preview');
    const userEmail = window.userEmail; // Ensure this is set in your HTML template

    generateBtn.addEventListener('click', function () {
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        fetch('../generate_avatar/generate_avatar.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: userEmail })
        })
        .then(async response => {
            let data;
            try {
                data = await response.json();
            } catch (e) {
                data = null;
            }
            if (data && data.status === 'ok') {
                let avatarPath = data.avatar_path;
                // If the backend returns only the filename, prepend the web path
                if (avatarPath && !avatarPath.startsWith('/')) {
                    avatarPath = '/2020FC/src/avatars/' + avatarPath;
                }
                avatarPreview.innerHTML = `<img id="generated-avatar-img" src="${avatarPath}?t=${Date.now()}" alt="Generated Avatar" style="max-width:300px;">`;
            } else {
                // Try to show the avatar anyway, in case it was generated
                const fallbackPath = `/2020FC/src/avatars/avatar_${userEmail}.png?t=${Date.now()}`;
                avatarPreview.innerHTML = `<img id="generated-avatar-img" src="${fallbackPath}" alt="Generated Avatar" style="max-width:300px;">`;
                // No error alert
            }
        })
        .catch(error => {
            // Try to show the avatar anyway, in case it was generated
            avatarPreview.innerHTML = `<img src="/2020FC/src/avatars/avatar_${userEmail}.png?t=${Date.now()}" alt="Generated Avatar" style="max-width:300px;">`;
            // No error alert
        })
        .finally(() => {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Avatar';
        });
    });
});
