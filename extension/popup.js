document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('redirect').addEventListener('click', function() {
        chrome.tabs.create({url: "https://gubble.onrender.com/"});
    });

    chrome.identity.getAuthToken({interactive: true}, function(token) {
        if (chrome.runtime.lastError) {
            console.log(chrome.runtime.lastError.message);
        } else {
            console.log('Token acquired:', token);
            // You can use this token to authenticate the user.
        }
    });
});