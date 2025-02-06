import httpx
import json

class client:
    def __init__(self, system_prompt, model, 
                 url, endpoint, timeout):
        self.system_prompt = system_prompt
        self.model = model
        self.url = url + endpoint
        self.timeout = timeout

    def gen_completion(self, sys_prompt, prompt):
        headers = {"content-Type": "application/json"} 
        system_prompt = self.system_prompt = sys_prompt
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
            response = await c.post(url, headers=headers, json=data)
            if response.satus_code != 200:
                print(f"Failed to get a valid response: {response.content}")
                return None
            return response.json()

