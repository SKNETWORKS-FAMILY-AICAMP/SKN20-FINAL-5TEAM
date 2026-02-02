import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.agent import run_problem_agent
try:
    print("Testing Agent Start...")
    # Very high level check
    from agent.spec import TRACK_SPECS
    print(f"Available Tracks: {list(TRACK_SPECS.keys())}")
    # run_problem_agent(track_id="pytorch_basic", max_retry=1) 
    # Don't run the whole thing, just check imports
    print("Import Success")
except Exception as e:
    print(f"Import/Setup Failed: {e}")
    import traceback
    traceback.print_exc()
