document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('redirect').addEventListener('click', function() {
        chrome.tabs.create({url: "https://gubble.onrender.com/"});
    });

    // chrome.identity.getAuthToken({interactive: true}, function(token) {
    //     if (chrome.runtime.lastError) {
    //         console.log(chrome.runtime.lastError.message);
    //     } else {
    //         console.log('Token acquired:', token);
    //         // You can use this token to authenticate the user.
    //     }
    // });
});

document.querySelector('#submitNumber').addEventListener('click', () => {
    const numberInput = document.querySelector('#numberInput');
    const number = numberInput.value;
    const button = document.querySelector('#submitNumber');

    console.log('Number:', number);
    console.log('URL:', `http://localhost:3000/get-data?id=${number}`);
    
    fetch(`http://localhost:3000/get-data?id=${number}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Data:', data);
            const dataElement = document.querySelector('#data');
            const table = document.createElement('table');

            const items = JSON.parse(data.message.replace(/'/g, '"'));

            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            ['Item Name', 'Description', 'Quantity', 'Expiry'].forEach(text => {
                const th = document.createElement('th');
                th.textContent = text;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement('tbody');
            items.forEach(item => {
                const row = document.createElement('tr');
                [item.item_name, item.description, item.quantity, item.expiry].forEach(text => {
                    const td = document.createElement('td');
                    td.textContent = text;
                    row.appendChild(td);
                });
                tbody.appendChild(row);
            });
            table.appendChild(tbody);
            dataElement.appendChild(table);
            button.style.display = 'none';
            numberInput.style.display = 'none';
        })
        .catch(error => {
            console.error('Error:', error);
        });
});