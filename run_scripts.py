import subprocess
import glob
import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.join(root_dir, 'src', 'api')
models_dir = os.path.join(root_dir, 'src', 'models')


def run(script):
    print(f'Running {os.path.relpath(script, root_dir)}...')
    # The scripts use paths relative to their own directory (../../data)
    subprocess.run([sys.executable, os.path.basename(script)], cwd=os.path.dirname(script), check=True)


# Run API scripts in order
api_scripts = [
    os.path.join(api_dir, 'get_election_results.py'),
    os.path.join(api_dir, 'get_counties.py'),
    os.path.join(api_dir, 'get_municipalities.py')
]

for script in api_scripts:
    run(script)

# Run all model scripts
for script in sorted(glob.glob(os.path.join(models_dir, '*.py'))):
    run(script)
