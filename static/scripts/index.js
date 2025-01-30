async function fetchChannels() {
    try {
        const response = await fetch('/channels');
        if (!response.ok) {
            throw new Error('Failed to fetch channels');
        }

        const channels = await response.json();
        const avatars = JSON.parse(document.getElementById('avatars-data').textContent);
        const channelsContainer = document.querySelector('.channels-list-wrapper');
        channelsContainer.innerHTML = ''; // Очищаем перед добавлением новых данных

        channels.forEach((channel, index) => {
            const card = document.createElement('a'); // Создаем <a>
            card.href = `/${channel}`; // Делаем всю карточку ссылкой
            card.classList.add('channel-card');

            const avatarImg = document.createElement('img');
            avatarImg.src = avatars[index];
            avatarImg.alt = `${channel} avatar`;
            avatarImg.classList.add('channel-avatar');

            const name = document.createElement('div');
            name.textContent = channel;
            name.classList.add('channel-name');

            card.appendChild(avatarImg);
            card.appendChild(name);
            channelsContainer.appendChild(card);
        });
    } catch (error) {
        console.error('Error occurred while fetching channels:', error);
    }
}

document.addEventListener('DOMContentLoaded', fetchChannels);
