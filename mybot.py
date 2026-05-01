def bot(**kwargs) -> str | list[str] | None:
    """
    Process messages and optionally return a reply.

    Args:
        kwargs keys currently provided:
            sender_name: Display name of sender (may be None)
            sender_key: 64-char hex public key (None for channel msgs)
            message_text: The message content
            is_dm: True for direct messages, False for channel
            channel_key: 32-char hex key for channels, None for DMs
            channel_name: Channel name with hash (e.g. "#bot"), None for DMs
            sender_timestamp: Sender's timestamp (unix seconds, may be None)
            path: Hex-encoded routing path (may be None)
            is_outgoing: True if this is our own outgoing message
            path_bytes_per_hop: Bytes per hop in path (1, 2, or 3) when known

    Returns:
        None for no reply, a string for a single reply,
        or a list of strings to send multiple messages in order
    """
    import requests
    
    sender_name = kwargs.get("sender_name")
    message_text = kwargs.get("message_text", "")
    channel_name = kwargs.get("channel_name")
    is_outgoing = kwargs.get("is_outgoing", False)
    path = kwargs.get("path")
    path_bytes_per_hop = kwargs.get("path_bytes_per_hop")

    # Don't reply to our own outgoing messages
    if is_outgoing:
        return None

    # Command handling
    msg_lower = message_text.lower().strip()
    
    # Remove ! prefix if present
    if msg_lower.startswith('!'):
        msg_lower = msg_lower[1:].strip()
    
    # Handle ping command
    if channel_name == "#mybot" and msg_lower == "ping":
        return " Pong!"
    
    # Handle test command with optional phrase
    if (channel_name == "#mybot" or channel_name == "#bot") and (
        msg_lower.startswith("test") or msg_lower == "t" or msg_lower.startswith("t ")
    ):
        # Extract phrase (remove 'test' or 't' prefix)
        if msg_lower.startswith("test"):
            phrase = msg_lower[4:].strip() if len(msg_lower) > 4 else ""
        else:  # starts with 't'
            phrase = msg_lower[1:].strip() if len(msg_lower) > 1 else ""
        
        response = f" Connection: {channel_name}"
        if sender_name:
            response += f" from {sender_name}"
        if phrase:
            response += f" | You said: '{message_text}'"
        return response
    
    # Handle path command - show the path info from the message
    if channel_name == "#mybot" and msg_lower == "path":
        if path:
            return f" Path: {path} | Bytes per hop: {path_bytes_per_hop}"
        else:
            return " No path data in this message"

    # Handle joke command
    if (channel_name == "#mybot" or channel_name == "#bot") and (
        msg_lower == "joke" or msg_lower == "dad joke" or msg_lower.startswith("joke ")
    ):
        try:
            # Fetch joke from API
            response = requests.get("https://official-joke-api.appspot.com/jokes/random")
            
            if response.status_code == 200:
                joke_data = response.json()
                
                # Extract setup and punchline
                # Using .get() ensures the bot doesn't crash if the API response is malformed
                setup = joke_data.get("setup")
                punchline = joke_data.get("punchline")

                if setup and punchline:
                    # Combined return to avoid blocking the thread or needing multiple sends
                    return f" {setup} ... {punchline}"
                else:
                    return " I found a joke, but it wasn't very funny (missing data). 😐"
            else:
                return " Joke service is currently down. Try again later!"
                
        except Exception as e:
            # Useful for debugging if the API structure changes
            return f" Error fetching joke: {str(e)}"

    return None
