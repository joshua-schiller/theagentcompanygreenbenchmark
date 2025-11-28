# Grader Guide: Running Green Agent Evaluator

This guide explains how to run the Green Agent parser and evaluator on white-agent trajectory outputs from TheAgentCompany benchmark.

## Quick Start

After a white-agent run completes, you can evaluate the trajectories using one of these methods:

### Option 1: Using the Helper Script (Recommended)

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

# Run full pipeline (parse + refine + evaluate)
make full-pipeline TRAJECTORY_DIR=/path/to/tac/outputs/results
```

### Option 3: Direct Python Commands

```bash
# Evaluate a single trajectory
python evaluator.py /path/to/traj_pm-schedule-meeting-1-image.json

# Evaluate all trajectories in a directory
python evaluator.py /path/to/tac/outputs/results --output results.json --report
```

## Reading Trajectories from TAC Outputs

The evaluator can read trajectories directly from TheAgentCompany output directories. Trajectory files follow the naming pattern `traj_*.json`.

### Mount Path Approach

If you're running in a containerized environment where TAC outputs are mounted:

```bash
# Assuming TAC outputs are mounted at /tac-results
python evaluator.py /tac-results --output /output/evaluation_results.json
```

### Copy Step Approach

If you need to copy trajectories first:

```bash
# Copy trajectory files to local directory
cp /path/to/tac/outputs/results/traj_*.json ./trajectories/

# Evaluate copied trajectories
python evaluator.py ./trajectories --output results.json
```

## Understanding Output

### Command-Line Output

The evaluator prints:
- **Efficiency Score** (0-100): Overall efficiency rating
- **Path Similarity** (0-1): How closely the agent path matches the golden path
- **Redundancy Penalty** (0-1): Penalty for duplicate/unnecessary actions
- **Path Length Ratio**: Ratio of agent path length to optimal path length

### JSON Output

When using `--output`, results are saved as JSON with:
- Task name and trajectory path
- Detailed scores
- Agent path (parsed actions)
- Golden path (optimal actions)
- Diagnostic report

Example:
```json
{
  "task_name": "pm-schedule-meeting-1",
  "scores": {
    "efficiency_score": 75.50,
    "path_similarity": 0.850,
    "redundancy_penalty": 0.200
  },
  "agent_path": [...],
  "golden_path": [...]
}
```

## Available Tasks

List all available tasks:
```bash
python evaluator.py --list-tasks
```

Current tasks:
- `pm-schedule-meeting-1`
- `sde-run-janusgraph`
- `hr-new-grad-job-description-3`
- `sde-create-new-repo`
- `pm-send-hello-message`
- `finance-qualified-bill-ask-for-reimburse`
- `ds-janusgraph-exercise`
- `ml-generate-gradcam`
- `research-answer-questions-on-paper`
- `qa-escalate-emergency`

## Detailed Reports

Get a detailed diagnostic report:
```bash
python evaluator.py trajectory.json --report
```

This shows:
- Component-by-component score breakdown
- Full action sequences (agent vs golden path)
- Summary of deviations and issues

## Troubleshooting

### No trajectory files found

Ensure trajectory files match the pattern `traj_*.json`. The evaluator automatically searches for files matching this pattern in the specified directory.

### Task name not recognized

Task names are extracted from filenames. Format: `traj_{task-name}-image.json` or `traj_{task-name}.json`

You can explicitly specify the task name:
```bash
python evaluator.py trajectory.json --task-name pm-schedule-meeting-1
```

### File not found errors

Check that:
1. The path to trajectories is correct
2. Files have read permissions
3. JSON files are valid (not corrupted)

## Advanced Usage

### Refining Golden Paths

If you need to refine golden paths based on new trajectories:

```bash
python refine_golden_paths.py \
  --task pm-schedule-meeting-1 \
  --trajectory /path/to/traj_pm-schedule-meeting-1-image.json \
  --save-json refinement_output.json
```

### Parsing Only

To just parse trajectories without evaluation:

```bash
python parser.py
```

This processes all `traj_*.json` files in the current directory and outputs to `parsed_actions_output.txt`.

## Integration with TAC Benchmark

The evaluator is designed to work seamlessly with TheAgentCompany benchmark outputs:

1. **After white-agent run**: Trajectory JSON files are generated in the results directory
2. **Run evaluator**: Point evaluator to the results directory
3. **Review scores**: Check efficiency scores and diagnostic reports

Example workflow:
```bash
# 1. Run white-agent (produces trajectories)
# ... white-agent execution ...

# 2. Evaluate trajectories
python evaluator.py /path/to/tac/results --output scores.json --report

# 3. Review results
cat scores.json | jq '.[] | {task: .task_name, score: .scores.efficiency_score}'
```

