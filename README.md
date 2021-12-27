# hackathon-client-server

#### Project description :
Server and client for an interactive quick math game, The point of the game is to answer correctly before your oponnent does.

#### Manual 📖:
1) Run `$python server.py` and type your preferred connection.
2) Run `$python client.py` on your client machine and enter your team's name.
3) Wait for an opponent and have fun! (╯°□°）╯︵ ┻━┻

#### Nerdy information 🤓:
The server starts by constantly broadcasting invites on a predetermined port. When the client recieves an offer it attempts to form a TCP connection and waits for an opponent to connect as well.
