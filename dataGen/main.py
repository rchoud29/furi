import asyncio
from client import Client

model = "meta-llama/Llama-3.1-8B-Instruct"
base_url = "https://8ul95u24yisw4z-8000.proxy.runpod.net/"
endpoint = "v1/chat/completions"
timeout = 30

prompt_base_prompt = ("You will be given a prompt. Please rewrite the prompt",
    " so that, when given to another LLM, its output will be as small",
    " as possible while still answering the prompt.\n",
    " For example, if a prompt is asking for an answer to calculations, you",
    " may want to append \"don't include calculations\" or ",
    " \"limit calculations\"",
    " Only include the new prompt without any other text"
    )

check_base_prompt = "You will be given a prompt and a response, please check\
 the quality of the response given and if the response answers the question\
 with an acceptable level of quality. Answer with \"Yes\" or \"No\" and no\
 other words.\nExample answers:\n\"Yes\"\n\"No\""

prompt_client = Client(prompt_base_prompt, model, base_url, endpoint, timeout)
check_client = Client(check_base_prompt, model, base_url, endpoint, timeout)

fail_shots = []

def construct_fail_shots():
    if (len(fail_shots) < 1): return ""
    prompt = "Here are some examples of prompts that are not optimized well \
and should not be followed: "
    for e in fail_shots:
        if e[0] == 'l':
            prompt += "\n Too long: " + e[1]
        elif e[0] == 'q':
            prompt += "\n Doesn't answer prompt: " + e[1]
    print("Prompt: " + prompt)
    return prompt

async def check_resp(check_client, prompt, response):
    check = await check_client.gen_completion("", "prompt: " +  prompt\
            + "\n" + "respons: " + response)
    check = check['choices'][0]['message']['content']
    return check


async def get_prompt(client, check_client, prompt, comp_rate):
    prompt_p = await client.gen_completion(construct_fail_shots(), prompt)
    prompt_p = prompt_p['choices'][0]['message']['content']
    print("\n" + prompt_p + "\n")
    
    resp = await client.gen_completion("", prompt, use_sys_prompt=False)
    resp = resp['choices'][0]['message']['content']
    resp_len = len(resp)

    resp_p = await client.gen_completion("", prompt_p, use_sys_prompt=False)
    resp_p = resp_p['choices'][0]['message']['content']
    resp_p_len = len(resp_p)
    
    if (resp_p_len/resp_len) > comp_rate:
        fail_shots.insert(0, ('l', prompt_p))
        print("failed: " + prompt_p)
        await get_prompt(client, check_client, prompt, comp_rate)
    else:
        check = await check_resp(check_client, prompt, resp_p)
        if check == "Yes":
            print(prompt_p)
            print("orig: " + resp)
            print("\n\nnew: " + resp_p)
            print(str(resp_p_len) + " vs " + str(resp_len) + ": "\
                + str(resp_p_len/resp_len))
            print(check)
        else:
            fail_shots.insert(0, ('q', prompt_p))
            await get_prompt(client, check_client, prompt, comp_rate)

asyncio.run(get_prompt(prompt_client, check_client, "I'm looking into getting a new hobby and I'm interested in the crafts. Can you explain crocheting and knitting and recommend one?", .8))
