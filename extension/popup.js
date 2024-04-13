document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('redirect').addEventListener('click', function() {
        chrome.tabs.create({url: "http://127.0.0.1:1111"});
    });
});

