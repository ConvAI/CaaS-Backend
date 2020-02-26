function includeCss(file) {
    const link = document.createElement('link');
    link.rel = "stylesheet";
    link.href = file;

    document.getElementsByTagName('head').item(0).appendChild(link);
}

function includeScript(file) {
    const script = document.createElement('script');
    script.src = file;
    script.type = 'text/javascript';
    script.defer = true;

    document.getElementsByTagName('body').item(0).appendChild(script);
}

//Load Css to Head
includeCss("{{loadurl}}/static/css/bootstrap.min.css");
includeCss("{{loadurl}}/static/css/magnific-popup.css");
includeCss("{{loadurl}}/static/css/circle.css");
includeCss("{{loadurl}}/static/css/chatbot.css");
includeCss("{{loadurl}}/static/css/typography.css");
includeCss("{{loadurl}}/static/css/style.css");
includeCss("{{loadurl}}/static/css/responsive.css");

//Add Chatbot to Body
const div = document.createElement('div');
div.id = 'chatbot_nervai';
div.insertAdjacentHTML('beforeend', '<div id="body" style="position: absolute;bottom: 5px;left: 5px;z-index: 1;">\n' +
    '    <div id="chat-circle" class="btn btn-raised">\n' +
    '        <i class="ion-chatbubble-working"></i>\n' +
    '    </div>\n' +
    '    <div class="chat-box">\n' +
    '        <div class="chat-box-header">\n' +
    '            <h5 class="title">ChatBot</h5>\n' +
    '            <span class="chat-box-toggle"><i class="ion-close-round"></i></span>\n' +
    '        </div>\n' +
    '        <div class="chat-box-body">\n' +
    '            <div class="chat-box-overlay">\n' +
    '            </div>\n' +
    '            <div class="chat-logs">\n' +
    '            </div>\n' +
    '            <!--chat-log -->\n' +
    '        </div>\n' +
    '        <div class="chat-input">\n' +
    '            <form>\n' +
    '                <input type="text" id="chat-input" placeholder="Send a message..."/>\n' +
    '                <button type="submit" class="chat-submit" id="chat-submit"><i class="ion-ios-paperplane"></i></button>\n' +
    '            </form>\n' +
    '        </div>\n' +
    '    </div>\n' +
    '</div>');
document.body.appendChild(div);

//Load Script to Init
includeScript("{{loadurl}}/static/js/jquery-3.3.1.min.js");
includeScript("{{loadurl}}/static/js/bootstrap.min.js");
includeScript("{{loadurl}}/static/js/popper.min.js");
includeScript("{{loadurl}}/static/js/owl.carousel.min.js");
includeScript("{{loadurl}}/static/js/wow.min.js");
includeScript("{{loadurl}}/static/js/app.min.js");
includeScript("{{loadurl}}/static/js/circle.js");
includeScript("{{loadurl}}/static/js/chatbot.js");
includeScript("{{loadurl}}/static/js/main.js");
includeScript("{{loadurl}}/static/js/custom.js");