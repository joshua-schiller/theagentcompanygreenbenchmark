# TheAgentCompany Green Agent

This repository contains the Green Agent implementation for TheAgentCompany benchmark, focusing on evaluating planning efficiency and resource-conscious behavior among AI agents.

## Overview

While the original TheAgentCompany benchmark evaluates task completion, our Green Agent evaluates **how efficiently** agents achieve goals by comparing their trajectories to "Golden Paths", which are optimal action sequences for each task.

## Features

- **Path Similarity Scoring**: Compares agent trajectories to golden paths using sequence alignment
- **Redundancy Detection**: Identifies and penalizes redundant or wasted actions
- **Diagnostic Reports**: Provides detailed analysis comparing agent paths to optimal paths
- **Modular Design**: Easy to extend with new tasks and golden paths

## Project Structure

```
theagentcompanygreenbenchmark/
├── parser.py              # Parses trajectory JSON logs into standardized actions
├── golden_paths.py        # Programmatic definitions of golden paths for all tasks
├── scoring.py             # Efficiency scoring algorithm
├── evaluator.py           # Main evaluation script
├── golden_paths_english.md # Descriptions of golden paths
├── refine_golden_paths.py # Helper script for refining golden paths
└── README.md              # This file
```

## Usage

### Basic Usage

Evaluate a single trajectory:

```bash
python evaluator.py traj_pm-schedule-meeting-1-image.json
```

Evaluate all trajectories in a directory:

```bash
python evaluator.py /path/to/trajectories/ --output results.json
```

### Command-Line Options

```bash
python evaluator.py --help
```

Options:
- `--task-name`: Specify task name explicitly (otherwise extracted from filename)
- `--output`: Save results to JSON file
- `--report`: Print detailed diagnostic report
- `--list-tasks`: List all available task names


## Tasks Evaluated

The Green Agent evaluates efficiency for 10 tasks:

1. **pm-schedule-meeting-1**: Schedule meeting between Emily Zhou and Liu Qiang
2. **sde-run-janusgraph**: Set up and run JanusGraph server
3. **hr-new-grad-job-description-3**: Create job description by gathering info
4. **sde-create-new-repo**: Create new GitLab repository
5. **pm-send-hello-message**: Send message to #general channel
6. **finance-qualified-bill-ask-for-reimburse**: Process reimbursement request
7. **ds-janusgraph-exercise**: Implement organizational chart in JanusGraph
8. **ml-generate-gradcam**: Generate GradCAM visualization
9. **research-answer-questions-on-paper**: Answer questions from research paper
10. **qa-escalate-emergency**: Escalate security vulnerability

## How It Works

### 1. Parsing Trajectories

The `parser.py` module converts raw trajectory JSON logs into standardized action strings:

- `execute_bash(command='...')` - Terminal commands
- `read_file(path='...')` - File reading
- `write_file(path='...')` - File writing
- `goto_url(url='...')` - Browser navigation
- `send_message(recipient='...', content='...')` - Chat messages
- `finish()` - Task completion

### 2. Golden Paths

Golden paths are defined in `golden_paths.py` as lists of standardized actions representing the optimal way to complete each task. These are manually curated based on:

- Task requirements
- Best practices
- Minimal necessary steps

### 3. Scoring Algorithm

The scoring algorithm (`scoring.py`) calculates:

- **Path Similarity** (0-1): How closely the agent path matches the golden path using sequence alignment
- **Redundancy Penalty** (0-1): Penalty for duplicate or unnecessary actions
- **Efficiency Score** (0-100): Overall score combining similarity and redundancy

### 4. Evaluation

The `evaluator.py` script:
1. Parses the agent trajectory
2. Retrieves the corresponding golden path
3. Calculates efficiency scores
4. Generates diagnostic reports

## Extending the Evaluator

### Adding a New Task

1. **Define Golden Path in English**: Add to `golden_paths_english.md`
2. **Create Programmatic Golden Path**: Add to `golden_paths.py`
3. **Test**: Run evaluator on sample trajectories


### Refining Golden Paths

Use `refine_golden_paths.py` to help refine golden paths based on actual parsed outputs:

```bash
python refine_golden_paths.py
```

Then manually update `golden_paths.py` with refined paths.

## Output Format

Evaluation results are saved as JSON with the following structure:

```json
{
  "task_name": "pm-schedule-meeting-1",
  "trajectory_path": "traj_pm-schedule-meeting-1-image.json",
  "scores": {
    "efficiency_score": 75.50,
    "path_similarity": 0.850,
    "redundancy_penalty": 0.200,
    "path_length_ratio": 1.20,
    "agent_path_length": 6,
    "golden_path_length": 5
  },
  "agent_path": [...],
  "golden_path": [...],
  "diagnostic_report": "..."
}
```


## Team

Team: Let's Get Sendyyy 67


