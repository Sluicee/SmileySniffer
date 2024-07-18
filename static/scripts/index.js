async function fetchChannels() {
    try {
        const response = await fetch('/channels');
        if (!response.ok) {
            throw new Error('Failed to fetch channels');
        }

        const channels = await response.json();
        const avatars = JSON.parse(document.getElementById('avatars-data').textContent); // Получаем массив аватаров из скрытого элемента
        const channelsTableBody = document.querySelector('#channels-table tbody');
        channelsTableBody.innerHTML = ''; // Очищаем таблицу перед добавлением новых данных

        channels.forEach((channel, index) => {
            const tr = document.createElement('tr');

            const avatarTd = document.createElement('td');
            const avatarImg = document.createElement('img');
            avatarImg.src = avatars[index]; // Используем соответствующий аватар
            avatarImg.alt = `${channel} avatar`;
            avatarTd.appendChild(avatarImg);
            tr.appendChild(avatarTd);

            const nameTd = document.createElement('td');
            const link = document.createElement('a');
            link.href = `/${channel}`;
            link.textContent = channel;
            nameTd.appendChild(link);
            tr.appendChild(nameTd);

            channelsTableBody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error occurred while fetching channels:', error);
    }
}

// Вызываем функцию fetchChannels при загрузке страницы
document.addEventListener('DOMContentLoaded', fetchChannels);
