import openai
import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed
import yaml
import os
# Feb 15, added my mark
# openai.api_key = os.environ['api_key']


class ProxyError(Exception):
    pass


async def get_answer(messages, use_proxy=False, **kwargs):
    try:
        response = await completion(use_proxy=use_proxy, messages=messages, temperature=1, max_tokens=1000, **kwargs)

        if 'err_msg_soc' in response:
            response = f"崩了，很可能是超出长度限制了！\n\n{response['err_msg_soc']}\n\n！"
        else:
            response = response['choices'][0]['message']['content']

    except openai.error.APIError as e:
        response = f"OpenAI API returned an API Error: {e}"

    except openai.error.RateLimitError as e:
        response = '问太多太快了，人家答不上来了！'

    except openai.error.Timeout as e:
        response = '人家脑慢了，一会儿再试试嘛！'

    except ProxyError as e:
        response = '代理田了！' + str(e)

    except Exception as e:
        response = '不知道为什么田了！\n\n' + str(e)

    finally:
        return response


async def get_answer_simple(text, use_proxy=False, **kwargs):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": text},
    ]

    return await get_answer(messages, use_proxy=use_proxy, **kwargs)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
async def completion(use_proxy=False, **kwargs):

    if use_proxy:
        url = kwargs['url']
        payload = {"model": "gpt-3.5-turbo", **kwargs}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    raise ProxyError(resp.status)

    else:
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", **kwargs)

        return response
