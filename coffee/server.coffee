net = require('net');

net.createServer( (socket) ->
  socket.name = socket.remoteAddress + ":" + socket.remotePort

  socket.write("Welcome " + socket.name + "\n");

  socket.on('data', (data) ->
    this.write("got: " + data)
  )

  socket.on('end', () ->
    console.log('user disconnected')
  )

).listen(5000)

console.log("Chat server running at port 5000\n");