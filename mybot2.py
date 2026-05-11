import random
from typing import Optional, Dict

def is_path_too_long(path_hex: str | None, bytes_per_hop: int | None) -> bool:
    """Check if the number of path hops exceeds 4"""
    if not path_hex or not bytes_per_hop:
        return False
    
    chars_per_hop = bytes_per_hop * 2
    
    if len(path_hex) % chars_per_hop != 0:
        return True  # Malformed path
    
    hop_count = len(path_hex) // chars_per_hop
    return hop_count > 4

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
    
    # 3. Channel restriction: ONLY respond in #mybot or #test
    if channel_name not in ["#mybot", "#test"]:
        return None
    
    # 4. Check path length
    if is_path_too_long(path, path_bytes_per_hop):
        return None

    # 5. Clean up the message
    msg_lower = message_text.lower().strip()
    if msg_lower.startswith('!'):
        msg_lower = msg_lower[1:].strip()
    
    # --- Commands Start Here ---
    
    # Handle help command
    if msg_lower == "help":
        return """Available commands:
ping - Check if bot is alive
test [phrase] - Test connection
path - Show routing path info
help - Show this message"""
    
    # Handle ping command
    if msg_lower == "ping":
        responses = ["PONG! 🏓", "ACK"]
        response = random.choice(responses)
        if sender_name: 
            response += f" @{sender_name}"
        return response
    
    # Handle test command
    if msg_lower.startswith("test") or msg_lower == "t" or msg_lower.startswith("t "):
        if msg_lower.startswith("test"):
            phrase = msg_lower[4:].strip()
        else:
            phrase = msg_lower[1:].strip()
        
        response = "@"
        if sender_name: 
            response += f" from {sender_name}"
        if phrase: 
            response += f" | You said: '{message_text}'"
        return response
    
    # Handle path command
    if msg_lower == "path":
        if path and path_bytes_per_hop:
            chars_per_hop = path_bytes_per_hop * 2
            
            if len(path) % chars_per_hop == 0:
                hop_count = len(path) // chars_per_hop
                hops = [path[i:i+chars_per_hop] for i in range(0, len(path), chars_per_hop)]
                formatted_path = " , ".join(hops)
                return f"Path: {formatted_path} | Bytes per hop: {path_bytes_per_hop} | Total hops: {hop_count}"
            else:
                return f"Path: {path} | Bytes per hop: {path_bytes_per_hop} | Invalid path format"
        return "No path data in this message"
    
    # No command matched
    return None
