let cachedEmotes = null;

    // Функция для получения и кэширования эмодзи
    async function fetchAndCacheEmotes() {
        if (!cachedEmotes) {
            try {
                // Попробуйте получить эмодзи
                const emotes = await fetchEmotes();
                if (emotes.length > 0) {
                    // Если данные эмодзи получены, сохраните их в кэше
                    cachedEmotes = emotes;
                    console.log('Emotes cached:', cachedEmotes); // Отладочный вывод
                }
            } catch (error) {
                console.error('Error occurred while fetching and caching emotes:', error);
            }
        }
        // Возвращаем кэшированные эмодзи (может быть пустым массивом, если они не были получены)
        return cachedEmotes;
    }

    
    // Получение сообщений с канала и их отображение
    async function fetchMessages() {
        try {
            const response = await fetch(`${channelName}/messages`);
            if (!response.ok) {
                throw new Error('Failed to fetch messages');
            }
    
            const messages = await response.json();
            console.log('Fetched Messages:', messages); // Отладочный вывод
    
            const messagesDiv = document.getElementById('chat-box');
            messagesDiv.innerHTML = '';  // Очищаем элемент перед началом цикла
    
            for (const msg of messages) {
                const div = document.createElement('div');
                div.className = 'chat-message';
                const words = msg.content.split(" ");
                let content = "";
    
                // Использование Promise.all для выполнения всех вызовов isEmote
                const wordPromises = words.map(async (wrd) => {
                    const emoteUrl = await isEmote(wrd);
                    return emoteUrl ? `<img src="${emoteUrl}">` : wrd;
                });
    
                const processedWords = await Promise.all(wordPromises);
                content = processedWords.join(" ");
    
                div.innerHTML = `${msg.author}: ${content}`;
                messagesDiv.insertBefore(div, messagesDiv.firstChild);  // Добавляем новый элемент в начало списка
            }
        } catch (error) {
            console.error('Error occurred while fetching messages:', error);
        }
    }
    
    // Получение эмодзи с канала и их отображение в таблице
    async function fetchEmotes() {
        try {
            const response = await fetch(`${channelName}/emotes`);
            if (!response.ok) {
                throw new Error('Failed to fetch emotes');
            }

            const emotes = await response.json();
            console.log('Fetched Emotes:', emotes); // Отладочный вывод

            const emotesTable = document.getElementById('emotes-table');
            emotesTable.innerHTML = ''; // Очищаем таблицу перед добавлением новых данных

            // В функции fetchEmotes() создаем блоки <div> для каждого эмодзи и его элементов
            emotes.forEach(emt => {
                // Создаем блок <div> для каждого эмодзи
                const emoteDiv = document.createElement('div');
                emoteDiv.className = 'emote';
            
                // Создаем блок <div> для изображения эмодзи
                const imgDiv = document.createElement('div');
                imgDiv.className = 'emote-img';
                const img = document.createElement('img');
                img.src = emt.data["host"]["url"] + "/" + emt.data["host"]["files"][3]["name"];
                imgDiv.appendChild(img);
                emoteDiv.appendChild(imgDiv);
            
                // Создаем блок <div> для имени эмодзи
                const nameDiv = document.createElement('div');
                nameDiv.className = 'emote-name';
                nameDiv.textContent = emt.data["name"];
                emoteDiv.appendChild(nameDiv);
            
                // Создаем блок <div> для счетчика
                const counterDiv = document.createElement('div');
                counterDiv.className = 'emote-counter';
                counterDiv.textContent = 0;
                emoteDiv.appendChild(counterDiv);
            
                // Добавляем блок эмодзи в контейнер emotes-table
                document.getElementById('emotes-table').appendChild(emoteDiv);
            });
            return emotes;
        } catch (error) {
            console.error('Error occurred while fetching emotes:', error);
            return [];
        }
    }
    
    // Проверка, является ли слово эмодзи
    async function isEmote(word) {
        try {
            const data = await fetchAndCacheEmotes();
            const emotes_list = data.reduce((acc, emt) => {
                acc[emt.data["name"]] = emt.data["host"]["url"] + "/" + emt.data["host"]["files"][1]["name"];
                return acc;
            }, {});
    
            const emoteUrl = emotes_list[word] || null;
            if (emoteUrl) {
                console.log(`Emote found for word "${word}": ${emoteUrl}`); // Отладочный вывод
            } else {
                console.log(`No emote found for word "${word}"`); // Отладочный вывод
            }
            return emoteUrl;
        } catch (error) {
            console.error('Error occurred while checking emote:', error);
            return null;
        }
    }
    

    //document.getElementById('send-form').addEventListener('submit', async (e) => {
      //e.preventDefault();
      //const channel = channelName;
      //const message = document.getElementById('message').value;
      //const response = await fetch('/send', {
        //method: 'POST',
        //headers: {
          //'Content-Type': 'application/json'
        //},
        //body: JSON.stringify({ channel, message })
      //});
      //if (response.ok) {
        //document.getElementById('message').value = '';
        //fetchMessages();
      //}
    //});
    document.addEventListener('DOMContentLoaded', () => {
        fetchMessages();
        fetchEmotes();
    });
    setInterval(fetchMessages, 1000);
    //setInterval(fetchEmotes, 3000);