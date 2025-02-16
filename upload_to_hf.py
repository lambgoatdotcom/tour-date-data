import json
from huggingface_hub import HfApi
import os
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def upload_to_huggingface(processed_data_path="tour_data_processed.json", images_dir="tour_images"):
    """Sync the processed data and tour images to Hugging Face datasets"""
    
    if not os.path.exists(processed_data_path):
        print(f"Error: {processed_data_path} not found. Please run process_dates.py first.")
        return

    try:
        # Get token from environment
        hf_token = os.getenv('HF_TOKEN')
        if not hf_token:
            raise ValueError("HF_TOKEN not found in environment variables")
            
        api = HfApi(token=hf_token)
        repo_id = "beatthetar/tour-dates"
        
        # Check/create repo
        try:
            repo_info = api.repo_info(repo_id=repo_id, repo_type="dataset")
            print(f"Using existing repository: {repo_id}")
        except Exception:
            print(f"Creating new repository: {repo_id}")
            api.create_repo(repo_id=repo_id, repo_type="dataset")

        # Get existing files
        existing_files = set(api.list_repo_files(repo_id=repo_id, repo_type="dataset"))
        local_files = {"data.json"}  # Start with our data file
        
        # Check if data.json needs updating
        if "data.json" in existing_files:
            # Download current version to compare
            api.hf_hub_download(repo_id=repo_id, repo_type="dataset", filename="data.json")
            if get_file_hash(processed_data_path) != get_file_hash("data.json"):
                print("Updating data.json...")
                api.upload_file(
                    path_or_fileobj=processed_data_path,
                    path_in_repo="data.json",
                    repo_id=repo_id,
                    repo_type="dataset",
                    commit_message="Update tour data"
                )
            else:
                print("data.json is up to date")
        else:
            print("Uploading data.json...")
            api.upload_file(
                path_or_fileobj=processed_data_path,
                path_in_repo="data.json",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message="Add tour data"
            )

        # Handle images
        if os.path.exists(images_dir):
            print("Syncing images...")
            for root, _, files in os.walk(images_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    repo_path = os.path.join(images_dir, file)
                    local_files.add(repo_path)
                    
                    # Check if file exists and needs updating
                    if repo_path in existing_files:
                        # Skip if file exists (assuming images don't change)
                        continue
                    else:
                        print(f"Uploading new image: {file}")
                        api.upload_file(
                            path_or_fileobj=filepath,
                            path_in_repo=repo_path,
                            repo_id=repo_id,
                            repo_type="dataset",
                            commit_message=f"Add image: {file}"
                        )

        # Delete files that no longer exist locally
        files_to_delete = existing_files - local_files - {"README.md"}
        for file in files_to_delete:
            print(f"Deleting removed file: {file}")
            api.delete_file(
                path_in_repo=file,
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"Delete {file}"
            )
        
        print(f"\nSuccessfully synced data to Hugging Face: https://huggingface.co/datasets/{repo_id}")
        
    except Exception as e:
        print(f"Error syncing to Hugging Face: {e}")

if __name__ == "__main__":
    upload_to_huggingface() 