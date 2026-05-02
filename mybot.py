
import requests
import random

def bot(**kwargs) -> str | list[str] | None:
    # 1. Get arguments from kwargs
    sender_name = kwargs.get("sender_name")
    message_text = kwargs.get("message_text", "")
    channel_name = kwargs.get("channel_name")
    is_outgoing = kwargs.get("is_outgoing", False)
    path = kwargs.get("path")
    path_bytes_per_hop = kwargs.get("path_bytes_per_hop")

    # 2. Safety check: Don't reply to ourselves
    if is_outgoing:
        return None

    # 3. Clean up the message
    msg_lower = message_text.lower().strip()
    if msg_lower.startswith('!'):
        msg_lower = msg_lower[1:].strip()
    
    # --- Commands Start Here (All Indented inside bot) ---

    # Handle help command
    if msg_lower == "help" or msg_lower == "?":
        return """Available commands:
!ping - Check if bot is alive
!test [phrase] - Test connection
!path - Show routing path info
!joke - Get a random joke
!help - Show this message"""
    
    # Handle ping command
    if (channel_name == "#mybot" or channel_name == "#bot") and msg_lower == "ping":
        responses = [
            "PONG! 🏓", "ACK!DCK", "yo poking me! 🤖",
            "Signal received.", "Yarp online.", "Echo... echo...",
            "What? I was busy.", "Pong! Did I win?", "01010000 01001111 01001110 01000111"
        ]
        return f"[BOT] {random.choice(responses)}"
    
    # Handle test command
    if (channel_name == "#mybot" or channel_name == "#bot") and (
        msg_lower.startswith("test") or msg_lower == "t" or msg_lower.startswith("t ")
    ):
        if msg_lower.startswith("test"):
            phrase = msg_lower[4:].strip()
        else:
            phrase = msg_lower[1:].strip()
        
        response = f" Connection: {channel_name}"
        if sender_name: response += f" from {sender_name}"
        if phrase: response += f" | You said: '{message_text}'"
        return response
    
    # Handle path command
    if channel_name == "#mybot" and msg_lower == "path":
        if path:
            return f" Path: {path} | Bytes per hop: {path_bytes_per_hop}"
        return " No path data in this message"

    # Handle joke command
    if (channel_name == "#mybot" or channel_name == "#bot") and (
        msg_lower == "joke" or msg_lower == "dad joke" or msg_lower.startswith("joke ")
    ):
        try:
            r = requests.get("https://official-joke-api.appspot.com/jokes/random", timeout=5)
            if r.status_code == 200:
                joke_data = r.json()
                setup = joke_data.get("setup")
                punchline = joke_data.get("punchline")
                return f" {setup} ... {punchline}"
            return " Joke service is currently down."
        except Exception as e:
            return f" Error fetching joke: {str(e)}"

    return None

Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
 
