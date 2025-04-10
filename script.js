window.onload = function() {

  // Get references to elements on the page.
  var form = document.getElementById('message-form');
  var messageField = document.getElementById('message');
  var messagesList = document.getElementById('messages');
  var socketStatus = document.getElementById('status');
  var closeBtn = document.getElementById('close');

  // Demander le pseudo à l'utilisateur
  var username = prompt('Entrez votre pseudo:', 'Utilisateur' + Math.floor(Math.random() * 1000));
  if (!username) {
    username = 'Anonyme' + Math.floor(Math.random() * 1000);
  }
  
  // Afficher le pseudo dans l'interface
  document.getElementById('username-display').textContent = username;

  // Create a new WebSocket with username in the URL
  var socket = new WebSocket('ws://51.44.59.58:7890/ws/' + username);


  // Handle any errors that occur.
  socket.onerror = function(error) {
    console.log('WebSocket Error: ' + error);
  };


  // Show a connected message when the WebSocket is opened.
  socket.onopen = function(event) {
    socketStatus.innerHTML = 'Connected to: ' + event.currentTarget.url;
    socketStatus.className = 'open';
  };


  // Handle messages sent by the server.
  socket.onmessage = function(event) {
    var message = event.data;
    
    try {
      // Essayer de parser le message comme JSON
      var parsedMessage = JSON.parse(message);
      
      // Vérifier si le message contient un objet avec text et sentiment
      if (parsedMessage.message && parsedMessage.message.text && parsedMessage.message.sentiment) {
        // Format du message diffusé par le serveur
        var text = parsedMessage.message.text;
        var sentiment = parsedMessage.message.sentiment;
        var username = parsedMessage.message.username || "Anonyme";
        var timestamp = parsedMessage.message.timestamp || new Date().toLocaleTimeString();
        
        // Ajouter une classe CSS basée sur le sentiment
        var sentimentClass = sentiment.toLowerCase();
        messagesList.innerHTML += '<li class="received ' + sentimentClass + '">' +
                              '<span class="timestamp">[' + timestamp + ']</span> ' +
                              '<span class="username">' + username + ':</span> ' +
                              text + ' <small>[Sentiment: ' + sentiment + ']</small></li>';
      } else if (parsedMessage.text && parsedMessage.sentiment) {
        // Format du message direct (non diffusé)
        var text = parsedMessage.text;
        var sentiment = parsedMessage.sentiment;
        
        // Ajouter une classe CSS basée sur le sentiment
        var sentimentClass = sentiment.toLowerCase();
        messagesList.innerHTML += '<li class="received ' + sentimentClass + '">' +
                              '<span class="timestamp">[' + new Date().toLocaleTimeString() + ']</span> ' +
                              '<span class="username">Vous:</span> ' +
                              text + ' <small>[Sentiment: ' + sentiment + ']</small></li>';
      } else {
  // Message au format texte simple
  messagesList.innerHTML += '<li class="received"><span>Received:</span>' + message + '</li>';
}
    } catch (e) {
      // Si le parsing échoue, afficher le message tel quel
      messagesList.innerHTML += '<li class="received"><span>Received:</span>' + message + '</li>';
    }
  };


  // Show a disconnected message when the WebSocket is closed.
  socket.onclose = function(event) {
    socketStatus.innerHTML = 'Disconnected from WebSocket.';
    socketStatus.className = 'closed';
  };


  // Send a message when the form is submitted.
  form.onsubmit = function(e) {
    e.preventDefault();

    // Retrieve the message from the textarea.
    var message = messageField.value;

    // Send the message through the WebSocket.
    socket.send(message);

    // Add the message to the messages list.
    messagesList.innerHTML += '<li class="sent"><span>Sent:</span>' + message + '</li>';

    // Clear out the message field.
    messageField.value = '';

    return false;
  };


  // Close the WebSocket connection when the close button is clicked.
  closeBtn.onclick = function(e) {
    e.preventDefault();

    // Close the WebSocket.
    socket.close();

    return false;
  };

};