# %% [markdown]
# # Agent Chat with Multimodal Models: DALLE  and GPT-4V
# 
# Requires: OpenAI V1. 

# %% [markdown]
# ### Before everything starts, install AutoGen with the `lmm` option
# ```bash
# pip install "pyautogen[lmm]~=0.2.0b4"
# ```

# %%
import requests
import json
import pdb
import os
import re

from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import autogen
from autogen import AssistantAgent, Agent, UserProxyAgent, ConversableAgent

from autogen.img_utils import get_image_data, _to_pil
from termcolor import colored
import random

# %%
from openai import OpenAI
import os
import PIL
import matplotlib.pyplot as plt

from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent


config_list = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": ["gpt-3.5-turbo"],
    },
)

config_list_4v = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": ["gpt-4-vision-preview"],
    },
)

config_list_gpt4 = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

config_list_dalle = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": ["dall-e-3"],
    },
)

gpt4_llm_config = {"config_list": config_list_gpt4, "cache_seed": 42}

# %% [markdown]
# The `config_list_dalle` should be something like:
# 
# ```python
# [
#     {
#         'model': 'dalle',
#         'api_key': 'Your API Key here',
#         'api_version': '2023-06-01-preview'
#     }
# ]
#  ```

# %% [markdown]
# ## Helper Functions
# 
# We first create a warpper for DALLE call, make the 

# %%
from diskcache import Cache

def dalle_call(client: OpenAI, model: str, prompt: str, size: str, quality: str, n: int) -> str:
    """
    Generate an image using OpenAI's DALL-E model and cache the result.

    This function takes a prompt and other parameters to generate an image using OpenAI's DALL-E model.
    It checks if the result is already cached; if so, it returns the cached image data. Otherwise,
    it calls the DALL-E API to generate the image, stores the result in the cache, and then returns it.

    Args:
        client (OpenAI): The OpenAI client instance for making API calls.
        model (str): The specific DALL-E model to use for image generation.
        prompt (str): The text prompt based on which the image is generated.
        size (str): The size specification of the image. TODO: This should allow specifying landscape, square, or portrait modes.
        quality (str): The quality setting for the image generation.
        n (int): The number of images to generate.

    Returns:
    str: The image data as a string, either retrieved from the cache or newly generated.

    Note:
    - The cache is stored in a directory named '.cache/'.
    - The function uses a tuple of (model, prompt, size, quality, n) as the key for caching.
    - The image data is obtained by making a secondary request to the URL provided by the DALL-E API response.
    """
    # Function implementation...
    cache = Cache('.cache/')  # Create a cache directory
    key = (model, prompt, size, quality, n)
    if key in cache:
        return cache[key]

    # If not in cache, compute and store the result
    response = client.images.generate(
          model=model,
          prompt=prompt,
          size=size,
          quality=quality,
          n=n,
        )
    image_url = response.data[0].url
    img_data = get_image_data(image_url)
    cache[key] = img_data

    return img_data



# %% [markdown]
# Here is a helper function to extract image from a DALLE agent. We will show the DALLE agent later.

# %%

def extract_img(agent: Agent) -> PIL.Image:
    """
    Extracts an image from the last message of an agent and converts it to a PIL image.

    This function searches the last message sent by the given agent for an image tag,
    extracts the image data, and then converts this data into a PIL (Python Imaging Library) image object.

    Parameters:
        agent (Agent): An instance of an agent from which the last message will be retrieved.

    Returns:
        PIL.Image: A PIL image object created from the extracted image data.

    Note:
    - The function assumes that the last message contains an <img> tag with image data.
    - The image data is extracted using a regular expression that searches for <img> tags.
    - It's important that the agent's last message contains properly formatted image data for successful extraction.
    - The `_to_pil` function is used to convert the extracted image data into a PIL image.
    - If no <img> tag is found, or if the image data is not correctly formatted, the function may raise an error.
    """
    # Function implementation...
    img_data = re.findall("<img (.*)>", agent.last_message()["content"])[0]
    pil_img = _to_pil(img_data)
    return pil_img


# %% [markdown]
# ## The DALLE Agent

# %%

class DALLEAgent(ConversableAgent):
    def __init__(self, name, llm_config: dict, **kwargs):
        super().__init__(name, llm_config=llm_config, **kwargs)
        
        try:
            config_list = llm_config["config_list"]
            api_key = config_list[0]["api_key"]
        except Exception as e:
            print("Unable to fetch API Key, because", e)
            api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        self.register_reply([Agent, None], DALLEAgent.generate_dalle_reply)
        
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        # override and always "silent" the send out message; 
        # otherwise, the print log would be super long!
        super().send(message, recipient, request_reply, silent=True)
        
    def generate_dalle_reply(self, messages: Optional[List[Dict]], sender: "Agent", config):
        """Generate a reply using OpenAI DALLE call."""
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]

        prompt = messages[-1]["content"]
        # TODO: integrate with autogen.oai. For instance, with caching for the API call
        img_data = dalle_call(
            client=self.client,
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024", # TODO: the size should be flexible, deciding landscape, square, or portrait mode.
            quality="standard",
            n=1,
        )
        out_message = f"<img {img_data}>"
        return True, out_message


# %% [markdown]
# ## Simple Example: Call directly from User

# %%
dalle = DALLEAgent(name="Dalle", llm_config={"config_list": config_list_dalle})

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0
)

# Ask the question with an image
user_proxy.initiate_chat(dalle,
                         message="""Create an image with black background, a happy robot is showing a sign with "I Love AutoGen".""", 
                         )

# %%
img = extract_img(dalle)

plt.imshow(img)
plt.axis('off')  # Turn off axis numbers
plt.show()

# %% [markdown]
# ## Example With Critics: Iterate several times to improve

# %%
class DalleCreator(AssistantAgent):

    def __init__(self, n_iters=2, **kwargs):
        """
        Initializes a DalleCreator instance.
        
        This agent facilitates the creation of visualizations through a collaborative effort among 
        its child agents: dalle and critics.
        
        Parameters:
            - n_iters (int, optional): The number of "improvement" iterations to run. Defaults to 2.
            - **kwargs: keyword arguments for the parent AssistantAgent.
        """
        super().__init__(**kwargs)
        self.register_reply([Agent, None],
                            reply_func=DalleCreator._reply_user,
                            position=0)
        self._n_iters = n_iters

    def _reply_user(self, messages=None, sender=None, config=None):
        if all((messages is None, sender is None)):
            error_msg = f"Either {messages=} or {sender=} must be provided."
            logger.error(error_msg)
            raise AssertionError(error_msg)

        if messages is None:
            messages = self._oai_messages[sender]

        img_prompt = messages[-1]["content"]

        ## Define the agents
        self.critics = MultimodalConversableAgent(
            name="Critics",
            system_message=
            """You need to improve the prompt of the figures you saw.
How to create a figure that is better in terms of color, shape, text (clarity), and other things.
Reply with the following format:

CRITICS: the image needs to improve...
PROMPT: here is the updated prompt!

""",
            llm_config={"config_list": config_list_4v, "max_tokens": 1000},
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
        )

        self.dalle = DALLEAgent(name="Dalle", llm_config={"config_list": config_list_dalle},     
                                max_consecutive_auto_reply=0)

        # Data flow begins
        self.send(message=img_prompt, recipient=self.dalle, request_reply=True)
        img = extract_img(self.dalle)
        plt.imshow(img)
        plt.axis('off')  # Turn off axis numbers
        plt.show()
        print("Image PLOTTED")
        
        
        for i in range(self._n_iters):
            # Downsample the image s.t. GPT-4V can take
            img = extract_img(self.dalle)
            smaller_image = img.resize((128, 128), Image.Resampling.LANCZOS)
            smaller_image.save("result.png")
            

            self.msg_to_critics = f"""Here is the prompt: {img_prompt}.
            Here is the figure <img result.png>.
            Now, critic and create a prompt so that DALLE can give me a better image.
            Show me both "CIRITICS" and "PROMPT"!
            """
            self.send(message=self.msg_to_critics,
                           recipient=self.critics,
                           request_reply=True)
            feedback = self._oai_messages[self.critics][-1]["content"]
            img_prompt = re.findall("PROMPT: (.*)", feedback)[0]
            
            self.send(
                message=img_prompt,
                recipient=self.dalle,
                request_reply=True)
            img = extract_img(self.dalle)
            plt.imshow(img)
            plt.axis('off')  # Turn off axis numbers
            plt.show()
            print(f"Image {i} PLOTTED")

        return True, "result.jpg"

# %%
import matplotlib.pyplot as plt
import time
from PIL import Image

creator = DalleCreator(
    name="DALLE Creator!",
    max_consecutive_auto_reply=0,
    system_message="Help me coordinate generating image",
    llm_config=gpt4_llm_config
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0
)

user_proxy.initiate_chat(creator,                         
                         message="""Create an image with black background, a happy robot is showing a sign with "I Love AutoGen".""")



