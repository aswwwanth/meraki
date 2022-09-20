function scrollToBottom() {
  $(".chat-body").scrollTop($(".chat-body")[0].scrollHeight);
}
var lastMessenger = null;
function addMessage(data, username) {
  var message_processed;
  // console.log(lastMessenger + " == " + data.username);
  if (data.username == lastMessenger) {
    if (data.username == username)
      message_processed = `<div class="message right-message" style="margin-top: -5px"><div class="message-container"><div class="message-content">${data.message}</div><div class="message-time">${data.time}</div></div></div>`;
    else
      message_processed = `<div class="message left-message"><div class="message-container" style="margin-left: 55px; margin-top: -15px"><div class="message-content">${data.message}</div><div class="message-time">${data.time}</div></div></div>`;
  } else if (data.username == username)
    message_processed = `<div class="message right-message"><div class="message-container"><div class="message-user">${data.username}</div><div class="message-content">${data.message}</div><div class="message-time">${data.time}</div></div></div>`;
  else
    message_processed = `<div class="message left-message"><div class="message-profile"><img src="/static/images/profile/${data[
      "username"
    ]
      .substr(0, 2)
      .toUpperCase()}.png"></div><div class="message-container"><div class="message-user">${
      data.username
    }</div><div class="message-content">${
      data.message
    }</div><div class="message-time">${data.time}</div></div></div>`;
  $(".chat-messages").append(message_processed);
  lastMessenger = data.username;
  scrollToBottom();
}

// Check scroll
$(".chat-body").scroll(function () {
  if (
    $(this).scrollTop() + $(this).innerHeight() + 5 <
    $(this)[0].scrollHeight
  ) {
    $(".chat-footer").css(
      "box-shadow",
      "0px -14px 25px -30px rgba(46,46,46,0.87)"
    );
  } else {
    $(".chat-footer").css("box-shadow", "0px 0px 0px 0px transparent");
  }
});
