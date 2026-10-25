# Project title: Compact Action Piano
MarinaHack 6.0 Project

# Inspiration:
Piano lovers that have no access to a physical one or are not affordable for one is the reason why we're building this project, especially for piano major students who have less access to lab compared to other science or engineering major. We're making a portable piano that can fit in a backpack, connecting to digital devices via bluetooth for a visualizer and speaker.

# What it does:
• Connect digital devices via Bluetooth by scanning device's name or server
• Running the web server while blocking anything might interrupt to listen to the piano notes
• Displays MIDI pitch into natural piano sounds
• Visualize a piano keyboard (7 lower keys and 5 upper keys)
• Displays the same keys and animations as the connected physical piano

# How we built it 
• Python Backend: Uses Flask and Bleak for background BLE scanning and connection handling, Flask-SocketIO keep track of the key's state
• HTML Frontend: Makes a light-purple themed visualizer built on HTML5 Canvas and CSS Flexbox. Use requestAnimationFrame in rendering loop to make the note pressing animation. Programs the piano pitch using Web Audio API matching standard calculations.

# Challenges we ran into
• In bleak, client.start_notify() expects a callback function with callback(sender, data), however, socket.emit() is synchronous when called from standard Python threads. We were facing difficulty while figuring out an approach to call async code inside. 
• We handled events across threads incorrectly
• We had problem running the connection retry continuously without blocking the running one
• Figure out how to detect sliding fingers across keys

# Accomplishments that we're proud of
• Successfully built a piano visualizer website with Bluetooth connection to digital devices

# What we learned
• Use a sleep interval in a while True loop ensures backend is resilient
• Advanced asynchronous Python uses asyncio and Bleak with WebSockets
• 2D HTML5 Canvas rendering techniques for real-time interaction and animation display
# What's next
