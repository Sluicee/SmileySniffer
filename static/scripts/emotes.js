let firstLoadCompleted = false; // Флаг для отслеживания первой загрузки

async function fetchEmotes() {
    try {
        const loadingOverlay = document.getElementById('loading-overlay');
        
        // Показываем анимацию загрузки только при первой загрузке
        if (!firstLoadCompleted) {
            loadingOverlay.style.display = 'block'; // Показать анимацию загрузки
        }
        
        const response = await fetch(`${channelName}/emotes`);
        if (!response.ok) {
            throw new Error('Failed to fetch emotes');
        }

        const responseJson = await fetch(`/download/${channelName}.json`);
        if (!responseJson.ok) {
            throw new Error('Network response was not ok ' + responseJson.statusText);
        }
        const dataEmotesCount = await responseJson.json();

        const emotes = await response.json();
        console.log('Fetched Emotes:', emotes); // Отладочный вывод

        // Сортировка эмодзи по убыванию значений в dataEmotesCount
        emotes.sort((a, b) => {
            const countA = dataEmotesCount[a.name] || 0;
            const countB = dataEmotesCount[b.name] || 0;
            return countB - countA; // Сортировка по убыванию
        });

        const emotesTableBody = document.querySelector('#emotes-table tbody');
        emotesTableBody.innerHTML = ''; // Очищаем таблицу перед добавлением новых данных

        emotes.forEach((emt, index) => {
            const tr = document.createElement('tr');

            const numberTd = document.createElement('td');
            numberTd.textContent = index + 1; // Добавляем порядковый номер
            tr.appendChild(numberTd);

            const imgTd = document.createElement('td');
            const img = document.createElement('img');
            img.src = emt.data["host"]["url"] + "/" + emt.data["host"]["files"][3]["name"];
            imgTd.appendChild(img);
            tr.appendChild(imgTd);

            const nameTd = document.createElement('td');
            nameTd.textContent = emt.name;
            tr.appendChild(nameTd);

            const counterTd = document.createElement('td');
            counterTd.textContent = dataEmotesCount[emt.name] || "0";
            tr.appendChild(counterTd);

            emotesTableBody.appendChild(tr);
        });

        // Добавляем обработчик события для поля поиска
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.trim().toLowerCase();

            emotes.forEach((emt, index) => {
                const emoteName = emt.name.toLowerCase();
                const tr = emotesTableBody.childNodes[index];

                if (emoteName.includes(searchTerm)) {
                    tr.style.display = ''; // Показываем строку, если она соответствует поисковому запросу
                } else {
                    tr.style.display = 'none'; // Скрываем строку, если она не соответствует
                }
            });
        });

        // Скрываем анимацию загрузки только после первой загрузки
        if (!firstLoadCompleted) {
            loadingOverlay.style.display = 'none'; // Скрыть анимацию загрузки
            firstLoadCompleted = true; // Устанавливаем флаг, что первая загрузка завершена
        }

        return emotes;
    } catch (error) {
        console.error('Error occurred while fetching emotes:', error);
        return [];
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchEmotes();
});
setInterval(fetchEmotes, 30000);
