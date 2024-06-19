async function fetchChannels() {
    try {
        const response = await fetch('/channels');
        if (!response.ok) {
            throw new Error('Failed to fetch channels');
        }

        const channels = await response.json();
        const channelsTableBody = document.querySelector('#channels-table tbody');
        channelsTableBody.innerHTML = ''; // Очищаем таблицу перед добавлением новых данных

        channels.forEach(channel => {
            const tr = document.createElement('tr');
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