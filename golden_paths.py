"""
Programmatic definitions of Golden Paths.

We define each Golden Path as a list of standardized action strings
that match the output format of the parser.
"""

# Task 1: pm-schedule-meeting-1
GOLDEN_PATH_PM_SCHEDULE_MEETING_1 = [
    "goto_url(url='http://the-agent-company.com:3000/home')",
    "send_message(recipient='Emily Zhou', content='...')",
    "send_message(recipient='Liu Qiang', content='...')",
    "write_file(path='/workspace/conclusion.txt')",
    "finish()"
]

# Task 2: sde-run-janusgraph
GOLDEN_PATH_SDE_RUN_JANUSGRAPH = [
    "execute_bash(command='cd /workspace && git clone http://the-agent-company.com:8929/root/janusgraph')",
    "execute_bash(command='cd /workspace/janusgraph && mvn clean install -DskipTests')",
    "execute_bash(command='cd /workspace/janusgraph && bin/janusgraph.sh start')",
    "finish()"
]

# Task 3: hr-new-grad-job-description-3
GOLDEN_PATH_HR_NEW_GRAD_JOB_DESCRIPTION_3 = [
    "read_file(path='/instruction/task.md')",
    "goto_url(url='http://the-agent-company.com:3000/home')",
    "send_message(recipient='Zhang Wei', content='...')",
    "send_message(recipient='Li Ming', content='...')",
    "read_file(path='/instruction/template.md')",
    "goto_url(url='http://the-agent-company.com:8092/')",
    "write_file(path='/Documents/job_description.md')",
    "write_file(path='/workspace/link.txt')",
    "finish()"
]

# Task 4: sde-create-new-repo
GOLDEN_PATH_SDE_CREATE_NEW_REPO = [
    "goto_url(url='http://the-agent-company.com:3000/')",
    "send_message(recipient='Zhang Wei', content='...')",
    "execute_bash(command='[create new GitLab repository via GitLab API or git commands]')",
    "write_file(path='/workspace/new-storage-project/README.md')",
    "finish()"
]

# Task 5: pm-send-hello-message
GOLDEN_PATH_PM_SEND_HELLO_MESSAGE = [
    "goto_url(url='http://the-agent-company.com:3000/home')",
    "goto_url(url='http://the-agent-company.com:3000/channel/general')",
    "send_message(content='[Hi and @active_users]')",
    "finish()"
]

# Task 6: finance-qualified-bill-ask-for-reimburse
GOLDEN_PATH_FINANCE_QUALIFIED_BILL = [
    "goto_url(url='http://the-agent-company.com:8092/')",
    "read_file(path='/Documents/Financials/receipt.jpg')",
    "read_file(path='/Documents/Administrative Specialist/Reimbursement Policy.pdf')",
    "goto_url(url='http://the-agent-company.com:3000/')",
    "send_message(recipient='Mike Chen', content='...')",
    "finish()"
]

# Task 7: ds-janusgraph-exercise
GOLDEN_PATH_DS_JANUSGRAPH_EXERCISE = [
    "execute_bash(command='cd /workspace && git clone http://the-agent-company.com:8929/root/janusgraph')",
    "execute_bash(command='cd /workspace/janusgraph && bin/janusgraph.sh start')",
    "read_file(path='/workspace/employee_diagram.jpg')",
    "write_file(path='/workspace/create_org_chart.py')",
    "execute_bash(command='cd /workspace && python create_org_chart.py')",
    "finish()"
]

# Task 8: ml-generate-gradcam
GOLDEN_PATH_ML_GENERATE_GRADCAM = [
    "goto_url(url='http://the-agent-company.com:8092/')",
    "read_file(path='/Documents/Research/test_image.jpg')",
    "write_file(path='/workspace/gradcam_script.py')",
    "execute_bash(command='cd /workspace && python gradcam_script.py')",
    "write_file(path='/workspace/gradcam_explanation.txt')",
    "finish()"
]

# Task 9: research-answer-questions-on-paper
GOLDEN_PATH_RESEARCH_ANSWER_QUESTIONS = [
    "goto_url(url='http://the-agent-company.com:8092/')",
    "read_file(path='/Documents/Research/Noise Simulation/noise_simulation_paper.pdf')",
    "read_file(path='/Documents/Research/Noise Simulation/noise_simulation_analysis_sheet.txt')",
    "write_file(path='/workspace/noise_simulation_analysis_sheet.txt')",
    "finish()"
]

# Task 10: qa-escalate-emergency
GOLDEN_PATH_QA_ESCALATE_EMERGENCY = [
    "goto_url(url='http://the-agent-company.com:3000/')",
    "send_message(recipient='Zhang Wei', content='...')",
    "send_message(recipient='Sarah Johnson', content='...')",
    "finish()"
]

# Map task names to their golden paths
GOLDEN_PATHS = {
    'pm-schedule-meeting-1': GOLDEN_PATH_PM_SCHEDULE_MEETING_1,
    'sde-run-janusgraph': GOLDEN_PATH_SDE_RUN_JANUSGRAPH,
    'hr-new-grad-job-description-3': GOLDEN_PATH_HR_NEW_GRAD_JOB_DESCRIPTION_3,
    'sde-create-new-repo': GOLDEN_PATH_SDE_CREATE_NEW_REPO,
    'pm-send-hello-message': GOLDEN_PATH_PM_SEND_HELLO_MESSAGE,
    'finance-qualified-bill-ask-for-reimburse': GOLDEN_PATH_FINANCE_QUALIFIED_BILL,
    'ds-janusgraph-exercise': GOLDEN_PATH_DS_JANUSGRAPH_EXERCISE,
    'ml-generate-gradcam': GOLDEN_PATH_ML_GENERATE_GRADCAM,
    'research-answer-questions-on-paper': GOLDEN_PATH_RESEARCH_ANSWER_QUESTIONS,
    'qa-escalate-emergency': GOLDEN_PATH_QA_ESCALATE_EMERGENCY,
}

def get_golden_path(task_name: str) -> list:
    """
    Get the golden path for a given task name.
    """
    return GOLDEN_PATHS.get(task_name, [])

def get_all_task_names() -> list:
    """Get a list of all task names."""
    return list(GOLDEN_PATHS.keys())

