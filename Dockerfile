{% if component == "Dockerfile" %}FROM python:{{ audit_results.python_version | default("3.9") }}-slim-buster

WORKDIR /app

COPY . /app

{% if audit_results.requirements_file_exists %}RUN pip install --no-cache-dir -r requirements.txt
{% endif %}
{% if audit_results.main_script %}CMD ["python", "{{ audit_results.main_script }}"]
{% endif %}{% elif component == "mlflow.yaml" %}tracking_uri: {{ audit_results.mlflow_tracking_uri | default("http://localhost:5000") }}
experiment_name: {{ audit_results.mlflow_experiment_name | default("Default Experiment") }}{% elif component == "Tests" %}import pytest
import sys
import os
from unittest.mock import patch

# Determine the path to the main script
# This assumes the test file is in a 'tests' directory and the main script is in the project root,
# or both are at the project root.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..')) # Try parent directory first

# Check if the main script exists in the assumed project_root
if not os.path.exists(os.path.join(project_root, "{{ audit_results.main_script }}")):
    # If not found in parent, assume the test file is at the project root itself
    project_root = current_dir

sys.path.insert(0, project_root)

# Extract module name from script name (e.g., 'train.py' -> 'train')
main_script_module_name = "{{ audit_results.main_script | replace('.py', '') }}"

try:
    # Import the main script as a module
    main_script = __import__(main_script_module_name)
except ImportError:
    pytest.fail(f"Could not import main script '{main_script_module_name}'. "
                f"Ensure '{{ audit_results.main_script }}' is in the project root "
                f"and that its dependencies are installed.")

def test_main_script_execution():
    """
    Test that the main script can be executed without raising unhandled exceptions.
    This test assumes the main script has a 'main' function or can be run directly.
    """
    # Mock sys.argv if the script processes command-line arguments
    with patch('sys.argv', ['python', '{{ audit_results.main_script }}']):
        try:
            # If the script defines a 'main' function, call it.
            if hasattr(main_script, 'main') and callable(main_script.main):
                main_script.main()
            else:
                # If no 'main' function, assume the script's top-level code
                # is intended to be executed upon import or via direct run.
                pass
            assert True, "Main script executed without unhandled exceptions."
        except SystemExit as e:
            # If the script calls sys.exit(), it might be a normal exit.
            # A non-zero exit code usually indicates an error.
            if e.code != 0:
                pytest.fail(f"Main script exited with non-zero status: {e.code}")
            assert True, "Main script exited successfully."
        except Exception as e:
            pytest.fail(f"Main script execution failed with an unexpected exception: {e}"){% endif %}