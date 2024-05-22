import json
import time
import random
from copy import deepcopy
import requests

try: GID
except NameError:
	GID = ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(8))
	print(f"Remote Tools: Set session ID to '{GID}'")

def get_client_id():
	global GID
	return(f"remote-tools-{GID}")

def get_new_job_id():
	job_id = f"{get_client_id()}-{int(time.time()*1000)}"
	time.sleep(0.1)
	return job_id

def dispatch_to_remote(remote_url, prompt, job_id=f"{get_new_job_id()}"):
	prompt = deepcopy(prompt)
	data = {
		"prompt": prompt,
		"client_id": get_client_id(),
		"extra_data": {
			"job_id": job_id,
		}
	}
	ar = requests.post(
		f"{remote_url}/prompt",
		data    = json.dumps(data),
		headers = {"Content-Type": "application/json"},
		timeout = 4,
	)
	ar.raise_for_status()
	data = ar.json()
	return data['prompt_id']

class SendBase64ToRemote:
    CATEGORY = "remote-tools"
    FUNCTION = "send_base64_to_remote"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base64": ("STRING", {"default": ""}),
                "remote_url": ("STRING", {"default": "http://127.0.0.1:8188"}),
                "remote_node_id": ("STRING", {"default": "1"}),
                "remote_node_input": ("STRING", {"default": "base64Images"}),
                "remote_prompt": ("STRING", {"multiline": True, "dynamicPrompts": False}),
            },
        }
    RETURN_TYPES = ()
    OUTPUT_NODE = True

    def send_base64_to_remote(self, base64, remote_url, remote_node_id, remote_node_input, remote_prompt):
        prompt = json.loads(remote_prompt)
        if remote_node_id in prompt:
            prompt[remote_node_id]['inputs'][remote_node_input] = base64
        prompt_id = dispatch_to_remote(remote_url, prompt)
        return ()

NODE_CLASS_MAPPINGS = {
    "SendBase64ToRemote" : SendBase64ToRemote,
}
