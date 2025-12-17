# TheAgentCompany Green Agent Benchmark

This project has two main parts: a Green Agent evaluator that scores how efficiently agents complete tasks, and a White Agent implementation that actually performs the tasks. The Green Agent compares agent trajectories to "golden paths" (optimal action sequences) to calculate efficiency scores.

## What's This About?

The original TheAgentCompany benchmark just checks if agents can complete tasks. This project adds a "Green Agent" evaluator that looks at HOW agents complete tasks - are they efficient? Do they waste steps? Do they follow optimal paths?

We also built a White Agent that tries to be more efficient by planning ahead, detecting redundant actions, and tracking goals. It doesn't see the golden paths (that would be cheating), but it uses better decision-making to avoid common problems like getting stuck in loops or missing steps.

## Project Structure

The main files:

- `evaluator.py` - Main script that evaluates agent trajectories
- `scoring.py` - The scoring algorithm (coverage, redundancy, path length, etc.)
- `parser.py` - Converts raw trajectory JSON into standardized actions
- `golden_paths.py` - Defines the optimal paths for each task
- `white_agent_intelligent.py` - Our white agent implementation
- `refine_golden_paths.py` - Helper script for refining golden paths
- `run_evaluation.sh` - Shell script to run evaluations
- `Makefile` - Convenience commands

## The Green Agent Evaluator

The evaluator takes trajectory JSON files from agent runs and scores them based on:

- Coverage: How many golden path steps were completed (60% of score)
- Order: Whether steps were done in the right sequence (15%)
- Path length: Penalty if the agent took way more steps than needed (10%)
- Redundancy: Penalty for repeating the same actions (15%)

### Running the Evaluator

After you have trajectory files from a white agent run, you can evaluate them:

```bash
# Evaluate a single trajectory
python evaluator.py traj_pm-schedule-meeting-1-image.json

# Evaluate all trajectories in a directory
python evaluator.py /path/to/trajectories/ --output results.json --report

# Or use the helper script
./run_evaluation.sh /path/to/trajectories --output results.json

# Or use the Makefile
make evaluate TRAJECTORY_DIR=/path/to/trajectories
```

The evaluator automatically finds all `traj_*.json` files in the directory. You can also use `--report` to get a detailed breakdown of what the agent did vs what it should have done.

### Tasks Evaluated

There are 10 tasks:

1. pm-schedule-meeting-1 - Schedule meeting between two people
2. sde-run-janusgraph - Set up and run JanusGraph server
3. hr-new-grad-job-description-3 - Create job description
4. sde-create-new-repo - Create new GitLab repository
5. pm-send-hello-message - Send message to general channel
6. finance-qualified-bill-ask-for-reimburse - Process reimbursement
7. ds-janusgraph-exercise - Implement org chart in JanusGraph
8. ml-generate-gradcam - Generate GradCAM visualization
9. research-answer-questions-on-paper - Answer questions from paper
10. qa-escalate-emergency - Escalate security issue

### How Scoring Works

1. The parser converts raw trajectory JSON into standardized actions like `execute_bash(command='...')`, `read_file(path='...')`, etc.

2. Golden paths are defined in `golden_paths.py` - these are the optimal sequences for each task, manually written based on task requirements.

3. The scoring algorithm aligns the agent's actions to the golden path and calculates:

   - Coverage: percentage of golden path steps that were matched
   - Order score: whether matched steps were in the right sequence
   - Length efficiency: penalty if agent path is much longer than golden path
   - Redundancy: detects repeated identical actions within a sliding window

4. Final efficiency score is a weighted combination of these components.

## The White Agent

Our white agent implementation (`white_agent_intelligent.py`) tries to be more efficient without seeing the golden paths. The main improvements are:

- **Task Analysis**: Extracts entities (people, files, URLs, commands) from the task description
- **Planning**: Creates a complete plan upfront instead of reacting step-by-step
- **Redundancy Detection**: Tracks recent actions and skips redundant ones to prevent loops
- **Goal Tracking**: Extracts goals from the task and only finishes when all are achieved
- **Task Classification**: Recognizes different task types (PM, SDE, HR, etc.) and uses appropriate patterns

The agent doesn't use golden paths - it reasons from the task description. But it fixes common problems that baseline agents have:

- Getting stuck sending the same message 25+ times
- Stopping early before completing all requirements
- Doing the wrong task entirely (like creating a Python project when it should set up JanusGraph)

### How the White Agent Works

1. **Task Analysis**: Reads `/instruction/task.md` and extracts entities (people mentioned, files to read, URLs to visit, commands to run)

2. **Planning**: Based on the task type and entities, creates a complete plan of actions

3. **Execution**: For each step:

   - Checks if the action is redundant (already done recently)
   - Executes the action
   - Reflects on the result and tracks which goals were achieved

4. **Completion**: Only finishes when all goals from the task are achieved

The key insight is that you don't need to see the "answers" (golden paths) to be better - you just need better decision-making to avoid common failure modes.

## Usage Examples

### Evaluating Trajectories

If you have trajectory files from a white agent run:

```bash
# Single file
python evaluator.py traj_pm-schedule-meeting-1-image.json --report

# All files in a directory
python evaluator.py /path/to/trajectories --output results.json

# Using the shell script
./run_evaluation.sh /path/to/trajectories --output results.json --report
```

### Output Format

Results are saved as JSON:

```json
{
  "task_name": "pm-schedule-meeting-1",
  "scores": {
    "efficiency_score": 75.50,
    "coverage": 0.850,
    "redundancy_penalty": 0.200,
    "path_length_ratio": 1.20
  },
  "agent_path": [...],
  "golden_path": [...]
}
```

## Extending the Evaluator

To add a new task:

1. Define the golden path in `golden_paths_descriptions.md` (human-readable)
2. Add the programmatic version to `golden_paths.py`
3. Test with sample trajectories

You can also use `refine_golden_paths.py` to help refine paths based on actual agent behavior:

```bash
python refine_golden_paths.py --task pm-schedule-meeting-1 --trajectory traj_pm-schedule-meeting-1-image.json
```

## Team

Team: Let's Get Sendyyy 67
