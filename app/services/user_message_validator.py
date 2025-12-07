import re

def is_valid_message(msg: str) -> bool:
    """Check if message is valid (not gibberish)."""
    msg = msg.strip().lower()
    
    # Basic checks
    if len(msg) < 1 or len(msg) > 500:  # Allow very short (e.g., "ok"), but cap long
        return False
    if not any(c.isalpha() for c in msg):  # No letters (e.g., "123!!!")
        return False
    
    # NEW: Allow common short valid messages
    valid_shorts = {"ok", "yes", "no", "hi", "hello", "hey", "bye", "thanks", "thank you"}
    if msg in valid_shorts:
        return True
    
    # NEW: Reject excessive repetition (e.g., "aaa", "lololol")
    if re.search(r'(.)\1{4,}', msg):  # 5+ repeats of same char
        return False
    
    # NEW: Reject mostly non-alphabetic or gibberish patterns
    # - All symbols/numbers with no words
    if re.match(r'^[^a-zA-Z]*$', msg):  # No letters at all
        return False
    # - High ratio of non-letters (e.g., "asdf123!!!")
    non_alpha_ratio = sum(1 for c in msg if not c.isalpha()) / len(msg)
    if non_alpha_ratio > 0.7:  # More than 70% non-letters
        return False
    
    # NEW: Reject known spam/gibberish patterns (customize as needed)
    spam_patterns = [
        r'\b(?:test|spam|fake)\b',  # Common spam words
        r'[a-z]{10,}',  # Very long words without spaces (likely gibberish)
    ]
    for pattern in spam_patterns:
        if re.search(pattern, msg):
            return False
    
    return True