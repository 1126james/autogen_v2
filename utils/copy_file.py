from pathlib import Path
import shutil

def CopyFile(source_file, destination_path):
    try:
        # Convert strings to Path objects
        source = Path(source_file)
        dest = Path(destination_path)
        
        # Ensure the destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(source, dest)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Source file '{source_file}' not found")
    except PermissionError:
        raise PermissionError("Permission denied. Check file and folder permissions")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")