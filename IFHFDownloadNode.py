import os
from huggingface_hub import hf_hub_download, snapshot_download
from server import PromptServer
from aiohttp import web

@PromptServer.instance.routes.post("/custom_node/hf_download")
async def hf_download_handler(request):
    post = await request.post()
    mode = post.get("mode")
    repo_id = post.get("repo_id")
    file_paths = post.get("file_paths")
    folder_path = post.get("folder_path")
    exclude_files = post.get("exclude_files")
    hf_token = post.get("hf_token")
    output = IFHFDownload().download_hf(mode, repo_id, file_paths, folder_path, exclude_files, hf_token)
    return web.json_response(output[0])

class IFHFDownload:
    def __init__(self):
        self.output = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repo_id": ("STRING", {"multiline": True}),
                "folder_path": ("STRING", {"multiline": True, "default": "folder in your computer to save the files"}),
                "hf_token": ("STRING", {"multiline": True, "default": "your Hugging Face token"}),
            },
            "optional": {
                "mode": ("BOOLEAN", {"default": False, "label_on": "All Repo", "label_off": "Individual Files"}),
                "file_paths": ("STRING", {"multiline": True, "default": ""}),
                "exclude_files": ("STRING", {"multiline": True, "default": ""}),
            },
            "widgets": {
                "download": ("BUTTON", {"text": "Download"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "download_hf"
    CATEGORY = "ImpactFrames💥🎞️"

    def download_hf(self, mode, repo_id, file_paths, folder_path, exclude_files, hf_token):
        exclude_list = [f.strip() for f in exclude_files.split(",") if f.strip()]

        if mode:
            # Download the entire repository
            snapshot_path = snapshot_download(repo_id=repo_id, local_dir=folder_path, repo_type="model", revision="main", token=hf_token)
            for root, dirs, files in os.walk(snapshot_path):
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), snapshot_path)
                    if file_path in exclude_list:
                        os.remove(os.path.join(root, file))
            self.output = f"Downloaded repo: {repo_id} to {os.path.normpath(snapshot_path)}"
        else:
            # Download individual files
            downloaded_files = []
            for file_path in file_paths.split(","):
                file_path = file_path.strip()
                if file_path:
                    filename = hf_hub_download(repo_id=repo_id, filename=file_path, local_dir=folder_path, token=hf_token)
                    downloaded_files.append(os.path.normpath(filename))
            if downloaded_files:
                self.output = f"Downloaded files: {', '.join(downloaded_files)} from {repo_id} to {os.path.normpath(folder_path)}"
            else:
                self.output = "No files were specified for download."

        return (self.output,)

NODE_CLASS_MAPPINGS = {"IF_HFDownload": IFHFDownload}
NODE_DISPLAY_NAME_MAPPINGS = {"IF_HFDownload": "Hugging Face Download🤗"}
