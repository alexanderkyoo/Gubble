document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('redirect').addEventListener('click', function() {
        chrome.tabs.create({url: "gubble.onrender.com"});
    });
});

