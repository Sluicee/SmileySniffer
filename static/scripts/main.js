// let cachedEmotes = null;
// let lastMessageTimestamp = 0; // Временная метка последнего обновления сообщений
// let sentEmotes = JSON.parse(localStorage.getItem('sentEmotes')) || {};

// // Функция для получения и кэширования эмодзи
// async function fetchAndCacheEmotes() {
//     if (!cachedEmotes) {
//         try {
//             const emotes = await fetchEmotes();
//             if (emotes.length > 0) {
//                 cachedEmotes = emotes;
//                 console.log('Emotes cached:', cachedEmotes); // Отладочный вывод
//             }
//         } catch (error) {
//             console.error('Error occurred while fetching and caching emotes:', error);
//         }
//     }
//     return cachedEmotes;
// }

// // Получение сообщений с канала и их отображение
// async function fetchMessages() {
//     try {
//         // Отправляем запрос только за сообщениями, полученными после последнего сообщения
//         const response = await fetch(`${channelName}/messages?since=${lastMessageTimestamp}`);
//         if (!response.ok) {
//             throw new Error('Failed to fetch messages');
//         }

//         const messages = await response.json();
//         console.log('Fetched Messages:', messages);

//         const messagesDiv = document.getElementById('chat-box');

//         for (const msg of messages) {
//             const messageTimestamp = new Date(msg.timestamp).getTime();
//             if (messageTimestamp <= lastMessageTimestamp) {
//                 continue; // Пропускаем старые сообщения
//             }

//             const div = document.createElement('div');
//             div.className = 'chat-message';
//             const words = msg.content.split(" ");
//             let content = "";

//             const wordPromises = words.map(async (wrd) => {
//                 const emoteUrl = await isEmote(wrd, channelName); // Передаем channelName
//                 return emoteUrl ? `<img src="${emoteUrl}">` : wrd;
//             });

//             const processedWords = await Promise.all(wordPromises);
//             content = processedWords.join(" ");

//             div.innerHTML = `${msg.author}: ${content}`;
//             messagesDiv.appendChild(div); // Добавляем новый элемент в конец списка
//         }

//         // Обновляем временную метку последнего сообщения
//         if (messages.length > 0) {
//             const lastMsgTimestamp = new Date(messages[messages.length - 1].timestamp).getTime();
//             lastMessageTimestamp = lastMsgTimestamp;
//             // Сохраняем временную метку в локальное хранилище
//             localStorage.setItem('lastMessageTimestamp', lastMessageTimestamp);
//         }
//     } catch (error) {
//         console.error('Error occurred while fetching messages:', error);
//     }
// }

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

        emotes.forEach(emt => {
            const tr = document.createElement('tr');

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




// // Проверка, является ли слово эмодзи
// async function isEmote(word, channelName) {
//     try {
//         const data = await fetchAndCacheEmotes();
//         const emotes_list = data.reduce((acc, emt) => {
//             acc[emt.data["name"]] = emt.data["host"]["url"] + "/" + emt.data["host"]["files"][1]["name"];
//             return acc;
//         }, {});

//         const emoteUrl = emotes_list[word] || null;
//         if (emoteUrl) {
//             console.log(`Emote found for word "${word}": ${emoteUrl}`); // Отладочный вывод
//             await sendWordToServer(word, channelName); // Отправка слова и канала на сервер, если оно является эмодзи
//         } else {
//             console.log(`No emote found for word "${word}"`); // Отладочный вывод
//         }
//         return emoteUrl;
//     } catch (error) {
//         console.error('Error occurred while checking emote:', error);
//         return null;
//     }
// }



// // Функция для отправки данных на сервер
// async function sendWordToServer(word, channelName) {
//     try {
//         const response = await fetch('/save_word', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({ 
//                 word: word, 
//                 channel: channelName,
//                 timestamp: new Date().toISOString() // Добавляем метку времени
//             })
//         });

//         if (!response.ok) {
//             throw new Error('Failed to send word to server');
//         }

//         const result = await response.json();
//         console.log('Success:', result);

//         // Получаем текущее время
//         const currentTime = new Date().toISOString();

//         // Помечаем смайлик как отправленный на сервер
//         sentEmotes[`${channelName}_${word}_${currentTime}`] = true;

//         // Сохраняем обновленные данные в локальное хранилище
//         localStorage.setItem('sentEmotes', JSON.stringify(sentEmotes));
//     } catch (error) {
//         console.error('Error occurred while sending word to server:', error);
//     }
// }

// document.addEventListener('DOMContentLoaded', () => {
//     const socket = io();  // Подключаемся к веб-сокет серверу

//     // Отправляем запрос на сервер для получения сообщений и обработка новых сообщений
//     async function fetchAndProcessMessages() {
//         try {
//             const response = await fetch(`${channelName}/messages?last_request_time=${lastMessageTimestamp}`);
//             if (!response.ok) {
//                 throw new Error('Failed to fetch messages');
//             }

//             const messages = await response.json();
//             console.log('Fetched Messages:', messages);

//             // Обрабатываем полученные сообщения
//             for (const msg of messages) {
//                 // Обработка сообщений...
//             }

//             // Обновляем временную метку последнего сообщения
//             if (messages.length > 0) {
//                 const lastMsgTimestamp = new Date(messages[messages.length - 1].timestamp).getTime();
//                 lastMessageTimestamp = lastMsgTimestamp;
//                 localStorage.setItem('lastMessageTimestamp', lastMessageTimestamp);
//             }
//         } catch (error) {
//             console.error('Error occurred while fetching messages:', error);
//         }
//     }

//     // Слушаем событие 'message' от сервера и обрабатываем полученные сообщения
//     socket.on('message', (data) => {
//         console.log('Received message:', data);
//         // Обработка полученных сообщений...
//     });

//     // Функция для отправки сообщения на сервер
//     async function sendMessageToServer(message) {
//         try {
//             // Отправляем сообщение на сервер через веб-сокет
//             socket.emit('message', { channel: channelName, message: message });
//         } catch (error) {
//             console.error('Error occurred while sending message to server:', error);
//         }
//     }

//     // Запрашиваем и обрабатываем сообщения сразу после загрузки страницы
//     fetchAndProcessMessages();

//     // Устанавливаем интервал для периодического обновления сообщений
//     setInterval(fetchAndProcessMessages, 1000);
// });


// setInterval(fetchMessages, 1000);
document.addEventListener('DOMContentLoaded', () => {
    fetchEmotes();
});
setInterval(fetchEmotes, 10000);
