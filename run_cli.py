# run_cli.py

import sys
import os
from agent_config import AgentContext  # Removed unused import AgentConfig
from initialize import initialize
from python.helpers.print_style import PrintStyle

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize context
context = AgentContext(config=initialize())

# Main loop
while True:
    try:
        # Get user input
        text = input("You: ")

        # Process input
        context.communicate(text)
        result = context.process_result()

        # Display result
        PrintStyle(font_color="green").print(f"Agent: {result}")

    except KeyboardInterrupt:
        print("\nExiting.")
        break

    except Exception as e:
        print(f"An error occurred: {e}")
        break
