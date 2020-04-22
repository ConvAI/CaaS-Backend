$(function() {
  let INDEX = 0;
  let isGreeted = false;
  let botMode = "chatbot";
  const URL = document.getElementById('chatbotscript').getAttribute('src').replace("/templatebot", "");
  const Botid = document.getElementById('chatbotscript').getAttribute('chatbot-id');
  const socket = io(URL);

  socket.on('connect', () => {});
  socket.on('disconnect', () => {socket.open();});
  socket.on('joinroom', (res) => {
    botMode = "adminbot";
    setTimeout(() => generate_message(res.msg, 'user'), 800);
    setTimeout(() => addLiveCircle(), 1000);
  });
  socket.on('leaveroom', (msg) => {
    botMode = "chatbot";
    setTimeout(() => generate_message(msg, 'user'), 800);
    setTimeout(() => removeLiveCircle(), 1000);
  });
  socket.on('adminAns', (msg) => {
    generate_message(msg, 'user');
  });

  $("#chat-submit").click(function(e) {
    e.preventDefault();
    const msg = $("#chat-input").val();
    if(msg.trim() === ''){
      return false;
    }
    generate_message(msg, 'self');
    if(botMode === "chatbot") {
        if (document.getElementById('chatbotscript').hasAttribute('previewbot')) {
          socket.emit("chatbot", {"BotId": Botid, "Question": msg, "Previewbot": 1}, (data) => {
              if(data.answer !== "[NIL]"){
                generate_message(data.answer, 'user');
              }
          });
        } else {
          socket.emit("chatbot", {"BotId": Botid, "Question": msg}, (data) => {
              if(data.answer !== "[NIL]"){
                generate_message(data.answer, 'user');
              }
          });
        }
    } else if(botMode === "adminbot") {
        socket.emit("adminQues", {"BotId": Botid, "Question": msg});
    }
  });

  function generate_message(msg, type) {
    INDEX++;
    var str="";
    str += "<div id='cm-msg-"+INDEX+"' class=\"chat-msg "+type+"\">";
    str += "          <div class=\"cm-msg-text\">";
    str += msg;
    str += "          <\/div>";
    str += "        <\/div>";
    $(".chat-logs").append(str);
    $("#cm-msg-"+INDEX).hide().fadeIn(300);
    if(type == 'self'){
		$("#chat-input").val(''); 
    }    
    $(".chat-logs").stop().animate({ scrollTop: $(".chat-logs")[0].scrollHeight}, 1000);    
  }  
  
  function generate_button_message(msg, buttons){    
    /* Buttons should be object array 
      [
        {
          name: 'Existing User',
          value: 'existing'
        },
        {
          name: 'New User',
          value: 'new'
        }
      ]
    */
    INDEX++;
    var btn_obj = buttons.map(function(button) {
       return  "              <li class=\"button\"><a href=\"javascript:;\" class=\"btn btn-primary chat-btn\" chat-value=\""+button.value+"\">"+button.name+"<\/a><\/li>";
    }).join('');
    var str="";
    str += "<div id='cm-msg-"+INDEX+"' class=\"chat-msg user\">";
    str += "          <span class=\"msg-avatar\">";
    str += "            <img src=\"https:\/\/image.crisp.im\/avatar\/operator\/196af8cc-f6ad-4ef7-afd1-c45d5231387c\/240\/?1483361727745\">";
    str += "          <\/span>";
    str += "          <div class=\"cm-msg-text\">";
    str += msg;
    str += "          <\/div>";
    str += "          <div class=\"cm-msg-button\">";
    str += "            <ul>";   
    str += btn_obj;
    str += "            <\/ul>";
    str += "          <\/div>";
    str += "        <\/div>";
    $(".chat-logs").append(str);
    $("#cm-msg-"+INDEX).hide().fadeIn(300);   
    $(".chat-logs").stop().animate({ scrollTop: $(".chat-logs")[0].scrollHeight}, 1000);
    $("#chat-input").attr("disabled", true);
  }
  
  $(document).delegate(".chat-btn", "click", function() {
    var value = $(this).attr("chat-value");
    var name = $(this).html();
    $("#chat-input").attr("disabled", false);
    generate_message(name, 'self');
  });
  
  $("#chat-circle").click(function() {
    if(!isGreeted){
      socket.emit("greetings", {"BotId": Botid}, (data) => {
          for(let i=0; i < data.len; i++){
              let msg = data.msgs[i];
              setTimeout(() => {
                generate_message(msg.msg, 'user');
              }, msg.delay);
          }
      });
      isGreeted = true;
    }
    $("#chat-circle").toggle('scale');
    $(".chat-box").toggle('scale');
  });
  
  $(".chat-box-toggle").click(function() {
    $("#chat-circle").toggle('scale');
    $(".chat-box").toggle('scale');
  });

  function addLiveCircle() {
    document.getElementById('titleid').textContent += "🟢";
  }

  function removeLiveCircle() {
    document.getElementById('titleid').textContent = "ChatBot";
  }
});