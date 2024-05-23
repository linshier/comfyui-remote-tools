import json
import time
import random
import uuid
from copy import deepcopy
import requests
import websocket

client_id = str(uuid.uuid4())

def get_client_id():
    global client_id
    return(f"remote-tools-{client_id}")

def get_new_job_id():
    job_id = f"{get_client_id()}-{int(time.time()*1000)}"
    time.sleep(0.1)
    return job_id

def dispatch_to_remote(remote_address, prompt, job_id=f"{get_new_job_id()}"):
    prompt = deepcopy(prompt)
    data = {
        "prompt": prompt,
        "client_id": get_client_id(),
        "extra_data": {
            "job_id": job_id,
        }
    }
    ar = requests.post(
        f"http://{remote_address}/prompt",
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
                "base64": ("STRING", {"forceInput": True}),
                "remote_address": ("STRING", {"default": "127.0.0.1:8188"}),
                "remote_node_id": ("STRING", {"default": "1"}),
                "remote_node_input": ("STRING", {"default": "base64Images"}),
                "remote_prompt": ("STRING", {"multiline": True, "dynamicPrompts": False}),
            },
        }
    RETURN_TYPES = ()
    OUTPUT_NODE = True

    def send_base64_to_remote(self, base64, remote_address, remote_node_id, remote_node_input, remote_prompt):
        prompt = json.loads(remote_prompt)
        if remote_node_id in prompt:
            prompt[remote_node_id]['inputs'][remote_node_input] = base64 # encoded([base64,])
        prompt_id = dispatch_to_remote(remote_address, prompt)
        return ()

class LoadBase64FromRemote:
    CATEGORY = "remote-tools"
    FUNCTION = "load_base64_from_remote"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "remote_address": ("STRING", {"default": "127.0.0.1:8188"}),
                "remote_node_id": ("STRING", {"default": "1"}),
                "remote_node_output": ("STRING", {"default": "base64Images"}),
                "remote_prompt": ("STRING", {"multiline": True, "dynamicPrompts": False}),
            },
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64",)

    def load_base64_from_remote(self, remote_address, remote_node_id, remote_node_output, remote_prompt):
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(remote_address, get_client_id()))

        job_id = get_new_job_id()
        prompt = deepcopy(json.loads(remote_prompt))
        prompt[f"{remote_node_id}@{job_id}"] = prompt.pop(remote_node_id) # avoid cache
        prompt_id = dispatch_to_remote(remote_address, prompt, job_id)

        base64= "[]"
        while True:
            out = ws.recv()
            if not isinstance(out, str):
                continue
            message = json.loads(out)
            if message['type'] not in ['executing', 'executed']:
                continue
            data = message['data']            
            if data['prompt_id'] == prompt_id:
                if data['node'] is None:
                	break #Execution is done
                if message['type'] != 'executed':
                    continue
                result = data['output'][remote_node_output]
                if isinstance(result, list): # [base64,]
                    base64 = json.JSONEncoder().encode(result)
                else:
                    base64 = result
                break
        ws.close()
        return (base64,)


NODE_CLASS_MAPPINGS = {
    "SendBase64ToRemote" : SendBase64ToRemote,
    "LoadBase64FromRemote" : LoadBase64FromRemote,
}
