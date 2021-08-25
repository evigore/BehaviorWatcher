const http = require("http");
const express = require( "express");
const WebSocket = require( "ws");

const app = express();

app.get("/metric", (req, res) => {
	res.sendFile(__dirname + "/index.html");
});

/*
const server = http.createServer(app);
const webSocketServer = new WebSocket.Server({ server });

webSocketServer.on('connection', ws => {
	ws.on('message', m => {
		m = JSON.parse(m);
		console.log(m);
		//webSocketServer.clients.forEach(client => client.send(m));
	});

	ws.on("error", e => ws.send(e));
	ws.send('Hi there, I am a WebSocket server');
});*/

server.listen(80, () => console.log("Server started"))
