#!/bin/bash
#
# Helper script to run the full Green Agent evaluation pipeline
# Usage: ./run_evaluation.sh <trajectory_dir_or_file> [options]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default values
TRAJECTORY_PATH=""
OUTPUT_FILE=""
REPORT_FLAG=""
TASK_NAME=""
RUN_REFINE=false
RUN_PARSE=false

# Parse arguments
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --report)
            REPORT_FLAG="--report"
            shift
            ;;
        --task-name)
            TASK_NAME="$2"
            shift 2
            ;;
        --refine)
            RUN_REFINE=true
            shift
            ;;
        --parse-only)
            RUN_PARSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 <trajectory_dir_or_file> [options]"
            echo ""
            echo "Options:"
            echo "  --output FILE          Save results to JSON file"
            echo "  --report              Print detailed diagnostic report"
            echo "  --task-name NAME      Specify task name explicitly"
            echo "  --refine              Also run golden path refinement"
            echo "  --parse-only          Only parse trajectories (no evaluation)"
            echo "  --help, -h            Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 /path/to/trajectories"
            echo "  $0 /path/to/trajectories --output results.json --report"
            echo "  $0 traj_pm-schedule-meeting-1-image.json --task-name pm-schedule-meeting-1"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Get trajectory path from positional args
if [ ${#POSITIONAL_ARGS[@]} -eq 0 ]; then
    echo "Error: Trajectory path required"
    echo "Use --help for usage information"
    exit 1
fi

TRAJECTORY_PATH="${POSITIONAL_ARGS[0]}"

# Check if trajectory path exists
if [ ! -e "$TRAJECTORY_PATH" ]; then
    echo "Error: Trajectory path does not exist: $TRAJECTORY_PATH"
    exit 1
fi

# Build evaluator command
EVAL_CMD="python evaluator.py \"$TRAJECTORY_PATH\""

if [ -n "$OUTPUT_FILE" ]; then
    EVAL_CMD="$EVAL_CMD --output \"$OUTPUT_FILE\""
fi

if [ -n "$REPORT_FLAG" ]; then
    EVAL_CMD="$EVAL_CMD $REPORT_FLAG"
fi

if [ -n "$TASK_NAME" ]; then
    EVAL_CMD="$EVAL_CMD --task-name \"$TASK_NAME\""
fi

# Run parse-only mode
if [ "$RUN_PARSE" = true ]; then
    echo "Running parser only..."
    if [ -d "$TRAJECTORY_PATH" ]; then
        # For directories, we need to handle this differently
        # The parser.py script processes files in current directory
        echo "Note: parser.py processes files in current directory"
        echo "Copying trajectory files to current directory..."
        cp "$TRAJECTORY_PATH"/traj_*.json . 2>/dev/null || {
            echo "Warning: No traj_*.json files found in $TRAJECTORY_PATH"
        }
    fi
    python parser.py
    exit 0
fi

# Run evaluation
echo "Running Green Agent Evaluator..."
echo "Trajectory path: $TRAJECTORY_PATH"
[ -n "$OUTPUT_FILE" ] && echo "Output file: $OUTPUT_FILE"
echo ""

eval $EVAL_CMD

# Optionally run refinement
if [ "$RUN_REFINE" = true ]; then
    echo ""
    echo "Running golden path refinement..."
    
    if [ -f "$TRAJECTORY_PATH" ]; then
        # Single file
        FILENAME=$(basename "$TRAJECTORY_PATH")
        TASK=$(echo "$FILENAME" | sed 's/traj_//' | sed 's/-image.json//' | sed 's/.json//')
        
        echo "Refining golden path for task: $TASK"
        python refine_golden_paths.py \
            --task "$TASK" \
            --trajectory "$TRAJECTORY_PATH" \
            --save-json "${TASK}_refinement.json" || {
            echo "Warning: Refinement failed or task name not recognized"
        }
    else
        echo "Note: Refinement requires a single trajectory file, not a directory"
        echo "Skipping refinement step"
    fi
fi

echo ""
echo "Evaluation complete!"

