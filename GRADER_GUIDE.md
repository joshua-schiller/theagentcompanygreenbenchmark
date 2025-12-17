# Grader Guide: Running the Evaluator

This explains how to run the Green Agent evaluator on white-agent trajectory outputs from TheAgentCompany benchmark.

## Quick Start

After a white-agent run completes, you can evaluate the trajectories. Here are a few ways to do it:

### Option 1: Using the Helper Script

```bash
# Evaluate all trajectories in a directory
./run_evaluation.sh /path/to/tac/outputs/results

# Or specify output file
./run_evaluation.sh /path/to/tac/outputs/results --output evaluation_results.json
```

### Option 2: Using Makefile

```bash
# Evaluate trajectories from a directory
make evaluate TRAJECTORY_DIR=/path/to/tac/outputs/results

# Evaluate a single trajectory file
make evaluate-single TRAJECTORY_FILE=/path/to/trajectory.json
```

### Option 3: Direct Python Command

```bash
# Evaluate a single trajectory
python evaluator.py /path/to/traj_pm-schedule-meeting-1-image.json

# Evaluate all trajectories in a directory
python evaluator.py /path/to/tac/outputs/results --output results.json --report
```

The evaluator automatically finds all `traj_*.json` files in the directory.

## Understanding Output

The evaluator prints:

- Efficiency Score (0-100): Overall efficiency rating
- Coverage: How many golden path steps were matched
- Redundancy Penalty (0-1): Penalty for duplicate/unnecessary actions
- Path Length Ratio: Ratio of agent path length to optimal path length

When using `--output`, results are saved as JSON with task name, scores, agent path, golden path, and diagnostic report.

## Available Tasks

List all available tasks:

```bash
python evaluator.py --list-tasks
```

There are 10 tasks:

- pm-schedule-meeting-1
- sde-run-janusgraph
- hr-new-grad-job-description-3
- sde-create-new-repo
- pm-send-hello-message
- finance-qualified-bill-ask-for-reimburse
- ds-janusgraph-exercise
- ml-generate-gradcam
- research-answer-questions-on-paper
- qa-escalate-emergency

## Detailed Reports

Get a detailed diagnostic report:

```bash
python evaluator.py trajectory.json --report
```

This shows component-by-component score breakdown, full action sequences (agent vs golden path), and summary of deviations.

## Troubleshooting

**No trajectory files found**: Make sure trajectory files match the pattern `traj_*.json`. The evaluator searches for files matching this pattern in the specified directory.

**Task name not recognized**: Task names are extracted from filenames. Format: `traj_{task-name}-image.json` or `traj_{task-name}.json`

You can explicitly specify the task name:

```bash
python evaluator.py trajectory.json --task-name pm-schedule-meeting-1
```

**File not found errors**: Check that the path is correct, files have read permissions, and JSON files are valid.

## Example Workflow

```bash
# 1. Run white-agent (produces trajectories)
# ... white-agent execution ...

# 2. Evaluate trajectories
python evaluator.py /path/to/tac/results --output scores.json --report

# 3. Review results
cat scores.json | jq '.[] | {task: .task_name, score: .scores.efficiency_score}'
```
