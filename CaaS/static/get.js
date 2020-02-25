
function include(file) { 
  
    var script  = document.createElement('script'); 
    script.src  = file; 
    script.type = 'text/javascript'; 
    script.defer = true; 
    
    document.getElementsByTagName('head').item(0).appendChild(script); 
    
} 

include("http://localhost:3232/static/js/jquery-3.3.1.min.js");
include("http://localhost:3232/static/js/bootstrap.min.js");
include("http://localhost:3232/static/js/popper.min.js");
include("http://localhost:3232/static/js/owl.carousel.min.js");
include("http://localhost:3232/static/js/wow.min.js");
include("http://localhost:3232/static/js/app.min.js");
include("http://localhost:3232/static/js/circle.js");
include("http://localhost:3232/static/js/chatbot.js");
include("http://localhost:3232/static/js/main.js");
include("http://localhost:3232/static/js/custom.js");
var url = document.getElementById('chatbotscript').getAttribute('src');
var data = document.getElementById('chatbotscript').getAttribute('data');
console.log(url)
console.log(data);
var div = document.createElement('div');
div.id = 'chatbot_nervai';
const xhr = new XMLHttpRequest();
xhr.open("GET", "http://localhost:3232/templatebot", true);
xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
        
        parser = new DOMParser();
        doc = parser.parseFromString(xhr.responseText, "text/html")
        div.insertAdjacentHTML('beforeend',xhr.responseText);      
        document.body.appendChild(div);
    }
};
xhr.send();
