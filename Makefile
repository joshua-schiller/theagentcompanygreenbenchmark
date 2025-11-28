.PHONY: help evaluate evaluate-single parse refine full-pipeline list-tasks clean

# Default Python interpreter
PYTHON := python3

# Default paths (can be overridden)
TRAJECTORY_DIR := .
TRAJECTORY_FILE := 
OUTPUT_FILE := results.json

help:
	@echo "Green Agent Evaluation Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make evaluate              - Evaluate all trajectories in TRAJECTORY_DIR"
	@echo "  make evaluate-single       - Evaluate a single trajectory file"
	@echo "  make parse                 - Parse all trajectories in current directory"
	@echo "  make refine                - Refine golden paths (requires TASK and TRAJECTORY_FILE)"
	@echo "  make full-pipeline         - Run parse + refine + evaluate"
	@echo "  make list-tasks            - List all available task names"
	@echo "  make clean                 - Remove generated output files"
	@echo ""
	@echo "Variables:"
	@echo "  TRAJECTORY_DIR=<path>      - Directory containing trajectory files"
	@echo "  TRAJECTORY_FILE=<path>     - Single trajectory file to evaluate"
	@echo "  OUTPUT_FILE=<path>         - Output JSON file (default: results.json)"
	@echo "  TASK=<name>                - Task name for refinement"
	@echo ""
	@echo "Examples:"
	@echo "  make evaluate TRAJECTORY_DIR=/path/to/tac/outputs"
	@echo "  make evaluate-single TRAJECTORY_FILE=traj_pm-schedule-meeting-1-image.json"
	@echo "  make full-pipeline TRAJECTORY_DIR=/path/to/tac/outputs OUTPUT_FILE=scores.json"
	@echo "  make refine TASK=pm-schedule-meeting-1 TRAJECTORY_FILE=traj_pm-schedule-meeting-1-image.json"

evaluate:
	@if [ -z "$(TRAJECTORY_DIR)" ]; then \
		echo "Error: TRAJECTORY_DIR not specified"; \
		exit 1; \
	fi
	@echo "Evaluating trajectories in: $(TRAJECTORY_DIR)"
	$(PYTHON) evaluator.py "$(TRAJECTORY_DIR)" --output "$(OUTPUT_FILE)" --report

evaluate-single:
	@if [ -z "$(TRAJECTORY_FILE)" ]; then \
		echo "Error: TRAJECTORY_FILE not specified"; \
		exit 1; \
	fi
	@echo "Evaluating trajectory: $(TRAJECTORY_FILE)"
	$(PYTHON) evaluator.py "$(TRAJECTORY_FILE)" --output "$(OUTPUT_FILE)" --report

parse:
	@echo "Parsing trajectories in current directory..."
	$(PYTHON) parser.py

refine:
	@if [ -z "$(TASK)" ] || [ -z "$(TRAJECTORY_FILE)" ]; then \
		echo "Error: TASK and TRAJECTORY_FILE must be specified"; \
		echo "Example: make refine TASK=pm-schedule-meeting-1 TRAJECTORY_FILE=traj_pm-schedule-meeting-1-image.json"; \
		exit 1; \
	fi
	@echo "Refining golden path for task: $(TASK)"
	$(PYTHON) refine_golden_paths.py \
		--task "$(TASK)" \
		--trajectory "$(TRAJECTORY_FILE)" \
		--save-json "$(TASK)_refinement.json"

full-pipeline:
	@if [ -z "$(TRAJECTORY_DIR)" ]; then \
		echo "Error: TRAJECTORY_DIR not specified"; \
		exit 1; \
	fi
	@echo "Running full evaluation pipeline..."
	@echo "Step 1: Parsing trajectories..."
	@if [ -d "$(TRAJECTORY_DIR)" ]; then \
		cp "$(TRAJECTORY_DIR)"/traj_*.json . 2>/dev/null || true; \
	fi
	$(PYTHON) parser.py
	@echo ""
	@echo "Step 2: Evaluating trajectories..."
	$(PYTHON) evaluator.py "$(TRAJECTORY_DIR)" --output "$(OUTPUT_FILE)" --report
	@echo ""
	@echo "Pipeline complete! Results saved to $(OUTPUT_FILE)"

list-tasks:
	@echo "Available tasks:"
	$(PYTHON) evaluator.py --list-tasks

clean:
	@echo "Cleaning generated files..."
	rm -f parsed_actions_output.txt
	rm -f results.json
	rm -f *_refinement.json
	@echo "Clean complete"

