var url = document.getElementById('chatbotscript').getAttribute('src');
console.log(url);
var div = document.createElement('div');
div.id = 'chatbot_nervai';
const xhr = new XMLHttpRequest();
xhr.open("GET", "http://localhost:3232/templatebot", true);
xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
        div.innerHTML = xhr.responseText;
    }
};
xhr.send();
document.body.appendChild(div);
