"""
Test script for Wordle reaction logic
"""
import re

def test_reaction_logic(message_content):
    """Test the reaction logic for a given message content"""
    print(f"Testing message:\n{message_content}\n")
    
    if "Wordle" not in message_content:
        print("No 'Wordle' in message, skipping")
        return
    
    lines = message_content.split('\n')
    if len(lines) < 2:
        print("Less than 2 lines, skipping")
        return
    
    header = lines[0]
    match = re.search(r'Wordle\s+([\d,]+)\s+([X\d]+)/6\*?', header)
    if not match:
        print("Header doesn't match regex, skipping")
        return
    
    attempts_str = match.group(2)
    solved = attempts_str != 'X'
    if solved:
        attempts = int(attempts_str)
    else:
        attempts = 7  # Failed
    
    # Check for no yellows in the grid
    grid_lines = [line for line in lines[1:] if line.strip() and any(c in line for c in ['🟩','🟨','⬛','⬜'])]
    has_yellow = any('🟨' in line for line in grid_lines)
    
    reactions = ["💯"]  # Always add this
    
    if not solved:
        reactions.append("😭")  # Failed
    else:
        if not has_yellow:
            reactions.append("🟩")  # Perfect solve
        
        # Placement reactions
        if attempts == 1:
            reactions.append("🥇")
        elif attempts == 2:
            reactions.append("🥈")
        elif attempts == 3:
            reactions.append("🥉")
    
    print(f"Reactions: {reactions}")
    print("-" * 50)

# Test cases
test_messages = [
    # Solved in 3 guesses, no yellows
    """Wordle 1,558 3/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟩🟩🟩""",
    
    # Solved in 2, with yellows
    """Wordle 1,559 2/6

🟨⬛⬛⬛⬛
🟩🟩🟩🟩🟩""",
    
    # Failed
    """Wordle 1,560 X/6

⬛⬛⬛⬛⬛
⬛🟨⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟩⬛⬛
🟩🟩🟩🟩⬛
🟩🟩🟩🟩🟩""",
    
    # Solved in 1
    """Wordle 1,561 1/6

🟩🟩🟩🟩🟩""",
    
    # Solved in 4, no yellows
    """Wordle 1,562 4/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟩⬛⬛
🟩🟩🟩🟩🟩"""
]

if __name__ == "__main__":
    for msg in test_messages:
        test_reaction_logic(msg)