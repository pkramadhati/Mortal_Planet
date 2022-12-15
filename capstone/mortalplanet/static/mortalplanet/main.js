//Aspects of the code below is based on solutions to problem sets on CSCI-E-33
let curMailbox = null;
let curMessage = null;



document.addEventListener('DOMContentLoaded', function () {

//Profile Nav Button Active
  const header = document.getElementById("profileNav");
  if (header) {
    const btns = header.getElementsByClassName("profile-nav-button");
    if (btns) {
      for (let i = 0; i < btns.length; i++) {
        btns[i].addEventListener("click", function () {
          const current = document.getElementsByClassName("active");
          current[0].className = current[0].className.replace(" active", "");
          this.className += " active";
        });
      }
    }
  }


 //SOURCE: www.youtube.com/watch?v=HpjW9eaFLIg

  //Get active page link 
  const navlink = document.querySelectorAll('.nav-link')
  navlink.forEach(link => {
    if (link.href === window.location.href) {
      link.setAttribute('aria-current', 'page')
      console.log(link.href)
    }
  })

  //inbox view
  const inbox = document.querySelector('#inbox')
  if (inbox) {
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#message-view').style.display = 'none';
    document.querySelector('#messages-view').style.display = 'none';

  }

  // compose message view 
  const compose = document.querySelector('#compose')
  if (compose) {
    compose.addEventListener('click', () => load_compose());
    document.querySelector('#compose-view').style.display = 'none';
  }



  //show myposts in profile
  const myposts = document.querySelector('#my-posts')
  if (myposts) {
    myposts.addEventListener('click', () => load_myposts());
    document.querySelector('#my-posts-view').style.display = 'none';
  }

  //show or hide open posts view
  const toggleopen = document.querySelector('#open-toggle')
  if (toggleopen) {
    toggleopen.addEventListener('click', () => load_openposts());
    document.querySelector('#open-posts-view').style.display = 'none';
    document.querySelector('#open-toggle').style.background = '#B3EFF8';
  }


  // When form is submitted, send a new message
  const submit = document.querySelector('#compose-form')
  if (submit) {
    submit.addEventListener('submit', send_message);
  }

  // Reply
  const reply = document.querySelector('#reply');
  if (reply) {
    reply.addEventListener('click', compose_reply);
  }
});


function add_message_to_mailbox(message) {

  // Create a new element for the message
  const row = document.createElement('div');
  row.classList.add('message-row');
  if (message.read) {
    row.classList.add('message-read');
  }

  console.log(curMailbox);
  if (curMailbox === "inbox") {
    row.innerHTML = `<strong>${message.sender}</strong> ${message.subject} <span class='message-timestamp'>${message.timestamp}</span>`;
  }

  else {
    row.innerHTML = `<strong>${message.recipients}</strong> ${message.subject} <span class='message-timestamp'>${message.timestamp}</span>`;
  }

  // When row is clicked on, show the message
  row.addEventListener('click', function () {
    show_message(message.id);
  });

  // Add row to the view
  document.querySelector('#messages-view').append(row);
}

// loads posts//

function load_openposts() {
  if (document.querySelector('#open-posts-view').style.display == 'none') {
    document.querySelector('#all-posts-view').style.display = 'none';
    document.querySelector('#open-posts-view').style.display = 'block';
    document.querySelector('#open-toggle').style.background = '#00CFFF';
  }
  else {
    document.querySelector('#all-posts-view').style.display = 'block';
    document.querySelector('#open-posts-view').style.display = 'none';
    document.querySelector('#open-toggle').style.background = '#B3EFF8';
  }

}

//loads mypost//

function load_myposts() {

  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#messages-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#profile-home').style.display = 'none';
  document.querySelector('#my-posts-view').style.display = 'block';

}

//loads compose// 

function load_compose() {

  document.querySelector('#my-posts-view').style.display = 'none';
  document.querySelector('#messages-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#profile-home').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

}


function load_mailbox(mailbox) {


  // Show the mailbox and hide other views
  curMailbox = mailbox;
  document.querySelector('#my-posts-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#profile-home').style.display = 'none';
  document.querySelector('#messages-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Query for latest messages
  fetch(`/messages/${mailbox}`)
    .then(response => response.json())
    .then(messages => {
      document.querySelector('#messages-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
      if (messages.length === 0) {
        document.querySelector('#messages-view').innerHTML += 'No messages in this mailbox.';
      }
      messages.forEach(add_message_to_mailbox);
    });
}

//sends message//

function send_message(event) {

  // Collect information about message from DOM
  const data = {
    recipients: document.querySelector('#compose-recipients').value,
    subject: document.querySelector('#compose-subject').value,
    body: document.querySelector('#compose-body').value
  };

  // Send API request to create new message
  fetch('/messages', {
    method: 'POST',
    body: JSON.stringify(data),
  })
    .then(response => response.json())
    .then(() => {
      document.querySelector('#compose-recipients').value = '';
      document.querySelector('#compose-subject').value = '';
      document.querySelector('#compose-body').value = '';
      console.log(document.querySelector('#compose-body').value)
    });
  event.preventDefault();
}


function compose_message() {

  // Show compose view and hide other views
  document.querySelector('#my-posts-view').style.display = 'none';
  document.querySelector('#messages-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#profile-home').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';


  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}


//reply 
function compose_reply() {

  // Start a new email
  compose_message();

  // Pre-fill recipients, subject, and body with standard reply-to information
  document.querySelector('#compose-recipients').value = curMessage.sender;
  document.querySelector('#compose-subject').value = curMessage.subject.slice(0, 4) === 'Re: ' ? curMessage.subject : `Re: ${curMessage.subject}`;
  document.querySelector('#compose-body').value = `\n\nOn ${curMessage.timestamp} ${curMessage.sender} wrote:\n${curMessage.body}`;
}

function show_message(message_id) {

  // Show the message view and hide the other views
  document.querySelector('#message-view').style.display = 'block';
  document.querySelector('#messages-view').style.display = 'none';
  document.querySelector('#profile-home').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Clear out message contents
  document.querySelector('#message-from').innerHTML = '';
  document.querySelector('#message-to').innerHTML = '';
  document.querySelector('#message-subject').innerHTML = '';
  document.querySelector('#message-timestamp').innerHTML = '';
  document.querySelector('#message-body').innerHTML = '';

  // Query for message details and fill data into DOM 
  fetch(`/messages/${message_id}`)
    .then(response => response.json())
    .then(message => {
      curMessage = message;
      document.querySelector('#message-from').appendChild(document.createTextNode(message.sender));
      document.querySelector('#message-to').appendChild(document.createTextNode(message.recipients));
      document.querySelector('#message-subject').appendChild(document.createTextNode(message.subject));
      document.querySelector('#message-timestamp').appendChild(document.createTextNode(message.timestamp));
      // document.querySelector('#message-body').appendChild(document.createTextNode(message.body));

      message.body.split('\n').forEach(line => {
        document.querySelector('#message-body').appendChild(document.createTextNode(line));
        document.querySelector('#message-body').appendChild(document.createElement('br'));
      })
    });

  // Mark message as read
  fetch(`/messages/${message_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  });
}


// 
// const activePage = window.location.pathname;
// const navLinks = document.querySelectorAll('.nav-link').forEach(link => {
//   if(link.href.includes(`${activePage}`)){
//     link.classList.add('active');
//     console.log(link);
//   }
// })
