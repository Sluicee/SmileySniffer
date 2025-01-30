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

        const responseStats = await fetch(`/api/${channelName}/stats`);
        if (!responseStats.ok) {
            throw new Error('Failed to fetch stats');
        }
        const dataEmotesCount = await responseStats.json();

        const responseEmotes = await fetch(`/${channelName}/emotes`);
        if (!responseEmotes.ok) throw new Error('Ошибка загрузки эмодзи');
        const emotes = await responseEmotes.json();
        console.log('Fetched Emotes:', emotes); // Отладочный вывод

        // Сортировка эмодзи по убыванию значений в dataEmotesCount
        emotes.sort((a, b) => {
            const countA = dataEmotesCount[a.name] || 0;
            const countB = dataEmotesCount[b.name] || 0;
            return countB - countA; // Сортировка по убыванию
        });

        // Обновление таблицы с новыми значениями
        updateEmotesTable(emotes, dataEmotesCount);

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

function updateEmotesTable(emotes, dataEmotesCount) {
    const emotesTableBody = document.querySelector('#emotes-table tbody');
    const fragment = document.createDocumentFragment(); // Создаем фрагмент в памяти

    // Создаем новые строки и добавляем их во фрагмент
    emotes.forEach((emt, index) => {
        const row = document.createElement('tr');

        // Столбец "Ранг"
        const rankTd = document.createElement('td');
        rankTd.textContent = index + 1;
        row.appendChild(rankTd);

        // Столбец "Изображение"
        const imgTd = document.createElement('td');
        const img = document.createElement('img');
        img.classList.add('lazy');
        img.dataset.src = emt.image_url; // Используем поле image_url из данных
        imgTd.appendChild(img);
        row.appendChild(imgTd);

        // Столбец "Название"
        const nameTd = document.createElement('td');
        nameTd.textContent = emt.name;
        row.appendChild(nameTd);

        // Столбец "Счетчик"
        const countTd = document.createElement('td');
        countTd.textContent = dataEmotesCount[emt.name] || "0";
        row.appendChild(countTd);

        fragment.appendChild(row); // Добавляем строку во фрагмент
    });

    // Вставляем все строки за одну операцию
    emotesTableBody.appendChild(fragment);
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

// Функция для сортировки таблицы
function sortTable(n) {
    const table = document.getElementById("emotes-table");
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const headers = table.querySelectorAll("thead th");
    const isAscending = table.dataset.sortDirection === 'asc';

    // Удаление классов сортировки с других заголовков
    headers.forEach(header => header.classList.remove('sort-asc', 'sort-desc'));

    // Добавление класса сортировки на текущий заголовок
    if (n !== 1) { // Не добавляем классы для столбца с изображением
        if (isAscending) {
            headers[n].classList.add('sort-asc');
        } else {
            headers[n].classList.add('sort-desc');
        }
    }

    rows.sort((a, b) => {
        const cellA = a.querySelectorAll("td")[n].textContent.trim();
        const cellB = b.querySelectorAll("td")[n].textContent.trim();

        let comparisonResult;

        // Если значения числовые
        if (!isNaN(cellA) && !isNaN(cellB)) {
            const numA = parseFloat(cellA);
            const numB = parseFloat(cellB);
            comparisonResult = numA - numB;
        } else {
            // Сравнение строковых значений
            comparisonResult = cellA.localeCompare(cellB);
        }

        // Если значения равны, сортировка по рангу в противоположном направлении
        if (comparisonResult === 0) {
            const rankA = parseInt(a.querySelectorAll("td")[0].textContent.trim(), 10); // Столбец Ранг
            const rankB = parseInt(b.querySelectorAll("td")[0].textContent.trim(), 10); // Столбец Ранг
            comparisonResult = rankA - rankB;

            // Инвертирование направления сортировки по рангу в зависимости от направления основной сортировки
            comparisonResult = -comparisonResult;
        }

        return isAscending ? comparisonResult : -comparisonResult;
    });

    tbody.innerHTML = "";
    rows.forEach(row => tbody.appendChild(row));

    table.dataset.sortDirection = isAscending ? 'desc' : 'asc';
}

document.addEventListener('DOMContentLoaded', () => {
    // Устанавливаем начальное состояние сортировки
    const table = document.getElementById("emotes-table");
    const headers = table.querySelectorAll("thead th");

    // Устанавливаем сортировку по возрастанию для столбца "Ранг"
    headers[0].classList.add('sort-asc');
    table.dataset.sortDirection = 'asc';

    sortTable(0)

    fetchEmotes();
    intervalId = setInterval(fetchEmotes, 30000); // Запускаем первый раз периодическое обновление данных
});
