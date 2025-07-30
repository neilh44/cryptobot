#!/usr/bin/env python
"""
Script to test the Crypto AI Agent interactively.
"""
import argparse
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

from app.agent.agent import CryptoAgent

async def main():
    """Main function to test the agent interactively."""
    parser = argparse.ArgumentParser(description="Test the Crypto AI Agent interactively.")
    parser.add_argument(
        "--session-id", "-s",
        type=str,
        default="test-session",
        help="Session identifier (default: test-session)"
    )
    
    args = parser.parse_args()
    
    print("Initializing Crypto AI Agent...")
    agent = CryptoAgent()
    
    print("\nCrypto AI Agent Ready!")
    print("Type 'exit' or 'quit' to end the session.")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending session. Goodbye!")
                break
            
            # Process the message
            print("\nAgent is thinking...")
            response = await agent.process_message(user_input)
            
            # Display the response
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            print("\nEnding session. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())