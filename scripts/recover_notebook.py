import json
import nbformat
import os
import shutil

try:
    # If 'notebooks' exists as a file, rename it temporarily
    if os.path.isfile('notebooks'):
        shutil.move('notebooks', 'notebooks.json')
    
    # Create notebooks directory if it doesn't exist
    os.makedirs('notebooks', exist_ok=True)
    
    # Read the original notebook content
    with open('notebooks.json' if os.path.exists('notebooks.json') else 'notebooks', 'r') as f:
        notebook_raw = f.read()

    # Parse the notebook content
    notebook_content = json.loads(notebook_raw)

    # Save as a proper .ipynb file
    with open('notebooks/insurance_analysis.ipynb', 'w') as f:
        json.dump(notebook_content, f, indent=2)

    print("Notebook successfully recovered and saved to notebooks/insurance_analysis.ipynb")

    # Clean up temporary file if it exists
    if os.path.exists('notebooks.json'):
        os.remove('notebooks.json')

except Exception as e:
    print(f"Error occurred: {str(e)}")
    print("Please ensure you have proper permissions and the notebooks file exists.") 