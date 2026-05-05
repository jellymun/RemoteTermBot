import requests
import random
import xml.etree.ElementTree as ET
from typing import Optional, Dict

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
    
    # 3. Check if path hops are greater than 4 (ignore message if true)
    def is_path_too_long(path_data: str | None) -> bool:
        """Check if the number of path hops exceeds 4"""
        if not path_data:
            return False
        
        # Split the path string and count hops (assuming path is comma or space separated)
        # Common path formats: "hop1,hop2,hop3" or "hop1 hop2 hop3"
        if ',' in path_data:
            hops = path_data.split(',')
        else:
            hops = path_data.split()
        
        # Count non-empty hops
        hop_count = len([hop for hop in hops if hop.strip()])
        return hop_count > 4
    
    # If path has more than 4 hops, ignore the message entirely
    if is_path_too_long(path):
        return None

    # 4. Clean up the message
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
!fdr [region] - Get Fire Danger Rating (defaults to Greater Sydney Region)
!help - Show this message"""
    
    # Handle ping command
    if (channel_name == "#mybot" or channel_name == "#bot") and msg_lower == "ping":
        responses = [
            "PONG! 🏓", "ACK!DCK", "yo poking me! 🤖",
            "Signal received.", "Yarp online.", "Echo... echo...",
            "What? I was busy.", "Pong! Did I win?", "01010000 01001111 01001110 01000111"
        ]
        response = random.choice(responses)
        if sender_name: 
            response += f" @{sender_name}"
        return response
    
    # Handle test command
    if (channel_name == "#mybot" or channel_name == "#bot") and (
        msg_lower.startswith("test") or msg_lower == "t" or msg_lower.startswith("t ")
    ):
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
    if channel_name == "#mybot" and msg_lower == "path":
        if path:
            # Calculate hop count for display
            if ',' in path:
                hops = path.split(',')
            else:
                hops = path.split()
            hop_count = len([hop for hop in hops if hop.strip()])
            
            return f" Path: {path} | Bytes per hop: {path_bytes_per_hop} | Total hops: {hop_count}"
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
                
                # Error handling for missing keys
                if setup is None or punchline is None:
                    return "jokes on Us; unable to connect"
                
                return f" {setup} ... {punchline}"
            return "jokes on Us; unable to connect"
        except Exception as e:
            return "jokes on Us; unable to connect"

    # Handle FDR command (Fire Danger Rating)
    if (channel_name == "#mybot" or channel_name == "#bot") and (
        msg_lower.startswith("fdr") or msg_lower.startswith("fire") or msg_lower.startswith("firedanger")
    ):
        # Constants for FDR command
        RFS_FEED_URL = "https://www.rfs.nsw.gov.au/feeds/fdrToban.xml"
        DEFAULT_DISTRICT_NAME = "Greater Sydney Region"
        MAX_TIMEOUT = 10
        
        # Helper functions for FDR
        def get_element_text(parent: ET.Element, tag_name: str) -> str:
            """Safely get text from a child element, or 'Unknown'."""
            element = parent.find(tag_name)
            return element.text.strip() if element is not None and element.text else 'Unknown'
        
        def fetch_fdr_data() -> Optional[ET.Element]:
            """Fetch and parse XML data from NSW RFS feed."""
            try:
                response = requests.get(RFS_FEED_URL, timeout=MAX_TIMEOUT)
                response.raise_for_status()
                return ET.fromstring(response.content)
            except (requests.RequestException, ET.ParseError):
                return None
        
        def extract_fdr_data(root: ET.Element, target_name: str) -> Optional[Dict[str, str]]:
            """Extract fire danger data for the specified district."""
            for district in root.findall('.//District'):
                name_text = get_element_text(district, 'Name')
                
                if name_text == target_name:
                    return {
                        'DangerLevelToday': get_element_text(district, 'DangerLevelToday'),
                        'FireBanToday': get_element_text(district, 'FireBanToday'),
                        'DangerLevelTomorrow': get_element_text(district, 'DangerLevelTomorrow'),
                        'FireBanTomorrow': get_element_text(district, 'FireBanTomorrow')
                    }
            return None
        
        def format_fdr_response(data: Dict[str, str], district_name: str) -> str:
            """Format fire danger data into a concise text message."""
            today_ban = "BAN" if data['FireBanToday'].lower() == 'yes' else "No ban"
            tomorrow_ban = "BAN" if data['FireBanTomorrow'].lower() == 'yes' else "No ban"
            
            return (f"🔥 {district_name}: Today {data['DangerLevelToday']} ({today_ban}), "
                   f"Tomorrow {data['DangerLevelTomorrow']} ({tomorrow_ban})")
        
        # Extract the region name from the command
        # Split the command (e.g., "fdr Greater Hunter" -> ["fdr", "Greater Hunter"])
        command_parts = msg_lower.split(maxsplit=1)
        
        # Default to Greater Sydney Region if no specific region provided
        target_region = DEFAULT_DISTRICT_NAME
        
        if len(command_parts) > 1:
            # Use the provided region name (preserve original case for better matching)
            # The original message_text has proper case, so use that for display
            # But for matching, we might need exact case as in XML
            if len(message_text.split(maxsplit=1)) > 1:
                target_region = message_text.split(maxsplit=1)[1].strip()
            else:
                target_region = command_parts[1].strip().title()
        
        # Fetch and process FDR data
        try:
            root = fetch_fdr_data()
            
            if root is None:
                return "❌ Failed to fetch fire danger data. The RFS feed might be unavailable."
            
            # Extract data for the target region
            data = extract_fdr_data(root, target_region)
            
            if data is None:
                # Try to find if there are any regions that might be close matches
                all_districts = []
                for district in root.findall('.//District'):
                    name_text = get_element_text(district, 'Name')
                    all_districts.append(name_text)
                
                if all_districts:
                    # Return a helpful error with available regions (limited to first 5 for brevity)
                    sample_regions = ', '.join(all_districts[:5])
                    if len(all_districts) > 5:
                        sample_regions += f", and {len(all_districts) - 5} more..."
                    return f"⚠️ Fire data for '{target_region}' not found. Available regions include: {sample_regions}"
                else:
                    return f"⚠️ Fire data for '{target_region}' not found in the feed."
            
            # Format and return the response
            return format_fdr_response(data, target_region)
            
        except Exception as e:
            return f"❌ An unexpected error occurred while processing fire data."

    return None
