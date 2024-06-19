// Получение эмодзи с канала и их отображение в таблице
async function fetchEmotes() {
    try {
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
        return emotes;
    } catch (error) {
        console.error('Error occurred while fetching emotes:', error);
        return [];
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchEmotes();
});
setInterval(fetchEmotes, 10000);
