"""
Test script to run the Wordle solver locally
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from services
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.wordle_solver import WordleSolver

async def main():
    print("🎯 Starting Wordle Solver Test...")
    print("-" * 50)

    solver = WordleSolver(headless=True)

    # Test the solver
    result = solver.solve(max_guesses=6)

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)

    if result:
        share_text = solver.capture_share_results()
        if share_text:
            print(f"✅ SUCCESS! Share text:\n{share_text}")
        else:
            print("✅ SUCCESS! But couldn't capture share text")
    else:
        print(f"❌ FAILED to solve")

    print(f"\n🎯 Guesses made: {len(solver.guesses)}")

if __name__ == "__main__":
    asyncio.run(main())
