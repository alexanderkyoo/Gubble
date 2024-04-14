document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('redirect').addEventListener('click', function() {
        chrome.tabs.create({url: "https://gubble.onrender.com/"});
    });
});

