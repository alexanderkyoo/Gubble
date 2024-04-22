// document.addEventListener('DOMContentLoaded', function () {
//     document.getElementById('redirect').addEventListener('click', function() {
//         chrome.tabs.create({url: "https://gubble.onrender.com/"});
//     });

//     chrome.identity.getAuthToken({interactive: true}, function(token) {
//         if (chrome.runtime.lastError) {
//             console.log(chrome.runtime.lastError.message);
//         } else {
//             console.log('Token acquired:', token);
//             // You can use this token to authenticate the user.
//         }
//     });
// });

fetch('http://localhost:3000/get-data')
    .then(response => response.json())
    .then(data => {
        // Select the element and display the data
        const dataElement = document.querySelector('#data');
        dataElement.textContent = JSON.stringify(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });