import json
import requests
import time
import typing
import textbase
from textbase.message import Message

class HuggingFace:
    api_key = "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";
from langchain import HuggingFaceHub
from langchain import PromptTemplate, LLMChain
import os
class OpenAI:
    api_key = None

    @classmethod
    def generate(
        cls,
        system_prompt: str,
        message_history: list[Message],
        model="gpt-3.5-turbo",
        max_tokens=3000,
        temperature=0.7,
    ):
        assert cls.api_key is not None, "OpenAI API key is not set"
        openai.api_key = cls.api_key

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                *map(dict, message_history),
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"]


class HuggingFace:

    @classmethod
    def generate(
        cls,
        system_prompt: str,
        message_history: list[Message],
        model: typing.Optional[str] = "microsoft/DialoGPT-small",
        max_tokens: typing.Optional[int] = 3000,
        temperature: typing.Optional[float] = 0.7,
        min_tokens: typing.Optional[int] = None,
        top_k: typing.Optional[int] = None
    ) -> str:
        try:
            assert cls.api_key is not None, "Hugging Face API key is not set"

            headers = {"Authorization": f"Bearer {cls.api_key}"}
            API_URL = "https://api-inference.huggingface.co/models/" + model
            inputs = {
                "past_user_inputs": [system_prompt],
                "generated_responses": [f"ok I will answer according to the context, where context is '{system_prompt}'"],
                "text": ""
            }
            
            for message in message_history:
                if message.role == "user":
                    inputs["past_user_inputs"].append(message.content)
                else:
                    inputs["generated_responses"].append(message.content)
            
            inputs["text"] = inputs["past_user_inputs"].pop(-1)
            payload = {
                "inputs": inputs,
                "max_length": max_tokens,
                "temperature": temperature,
                "min_length": min_tokens,
                "top_k": top_k,
            }
            data = json.dumps(payload)
            response = requests.post(API_URL, headers=headers, json=payload)
            response_data = response.json()

            if response_data.get("error", None) == "Authorization header is invalid, use 'Bearer API_TOKEN'":
                print("Hugging Face API key is not correct")

            if response_data.get("estimated_time", None):
                print(f"Model is loading, please wait for {response_data.get('estimated_time')} seconds")
                time.sleep(response_data.get("estimated_time"))
                response = requests.post(API_URL, headers=headers, json=payload)
                response_data = response.json()

            return response_data["generated_text"]
        except Exception as ex:
            print(f"Error occured while using this model, please try using another model, Exception was {ex}")

class BotLibre:
    application = None
    instance = None

    @classmethod
    def generate(
        cls,
        message_history: list[Message],
    ):
        request = {"application":cls.application, "instance":cls.instance,"message":message_history[-1].content}
        response = requests.post('https://www.botlibre.com/rest/json/chat', json=request)
        data = json.loads(response.text) # parse the JSON data into a dictionary
        message = data['message']
        return message

class LangchainHuggingFace:
    api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    @classmethod
    def generate(
        cls,
        message_history: list[Message],
        system_prompt: str,
        model: typing.Optional[str] = "databricks/dolly-v2-3b",
        max_tokens: typing.Optional[int] = 100,
        temperature: typing.Optional[float] = 0.9,
        min_tokens: typing.Optional[int] = None,
        top_k: typing.Optional[int] = 50
        ) -> str:
            try:
                assert cls.api_key is not None, "Hugging Face API key is not set"

                hub_llm = HuggingFaceHub(repo_id=model, model_kwargs={"temperature": temperature, "max_length": max_tokens, "top_k": top_k})
                message = message_history[-1].content
                template = """Chat with me, """ + system_prompt + """ I say: {message} 
                """
                prompt = PromptTemplate(template=template, input_variables=["message"])
                llm_chain = LLMChain(prompt=prompt, llm=hub_llm, verbose=True)
                
                response = llm_chain.run(message=message)
                
                return response
            except Exception as ex:
                print(f"Error occured while using this model, please try using another model, Exception was {ex}")
