import httpx
import json

class Client:
    def __init__(self, system_prompt: str, model, 
                 url, endpoint, timeout):
        self.system_prompt = system_prompt
        self.model = model
        self.url = url + endpoint
        self.timeout = timeout

    async def gen_completion(self, sys_prompt, prompt, use_sys_prompt=True):
        headers = {"content-Type": "application/json"} 
        system_prompt = "".join(self.system_prompt) + (sys_prompt if sys_prompt is not None else "")
        if not use_sys_prompt:
            system_prompt = "You are a helpful assistant"

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "stop": "<|eot_id|>"
        }
        timeout = httpx.Timeout(self.timeout)

        async with httpx.AsyncClient(timeout=timeout) as c:
            response = await c.post(self.url, headers=headers, json=data)
            if response.status_code != 200:
                print(f"Failed to get a valid response: {response.content}")
                return None
            return response.json()

