let firstLoadCompleted = false; // Флаг для отслеживания первой загрузки
let searchTerm = ''; // Переменная для хранения текущего поискового запроса
let intervalId = null; // Переменная для хранения ID интервала

async function fetchEmotes() {
    try {
        const loadingOverlay = document.getElementById('loading-overlay');
        
        // Показываем анимацию загрузки только при первой загрузке или при регулярном обновлении
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
            img.classList.add('lazy');
            img.dataset.src = emt.data["host"]["url"] + "/" + emt.data["host"]["files"][3]["name"];
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
        searchInput.removeEventListener('input', handleSearch);
        searchInput.addEventListener('input', handleSearch);

        // Скрываем анимацию загрузки только после первой загрузки или при регулярном обновлении
        if (!firstLoadCompleted) {
            loadingOverlay.style.display = 'none'; // Скрыть анимацию загрузки
            firstLoadCompleted = true; // Устанавливаем флаг, что первая загрузка завершена
        }

        // Инициализируем ленивую загрузку изображений
        const lazyLoadImages = document.querySelectorAll("img.lazy");

        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const image = entry.target;
                    image.src = image.dataset.src;
                    image.classList.remove("lazy");
                    observer.unobserve(image);
                }
            });
        });

        lazyLoadImages.forEach(image => {
            imageObserver.observe(image);
        });

        return emotes;
    } catch (error) {
        console.error('Error occurred while fetching emotes:', error);
        return [];
    }
}

function handleSearch() {
    searchTerm = this.value.trim().toLowerCase();
    
    // Если активный поисковый запрос, останавливаем периодическое обновление данных
    if (searchTerm !== '') {
        clearInterval(intervalId);
        intervalId = null;
    } else {
        // Восстанавливаем периодическое обновление данных, если было остановлено
        if (intervalId === null) {
            intervalId = setInterval(fetchEmotes, 30000);
        }
    }

    // Фильтрация и отображение эмодзи в таблице
    const emotesTableBody = document.querySelector('#emotes-table tbody');
    const rows = emotesTableBody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const emoteName = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
        if (emoteName.includes(searchTerm)) {
            row.style.display = ''; // Показываем строку, если она соответствует поисковому запросу
        } else {
            row.style.display = 'none'; // Скрываем строку, если она не соответствует
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    fetchEmotes();
    intervalId = setInterval(fetchEmotes, 30000); // Запускаем первый раз периодическое обновление данных
});
