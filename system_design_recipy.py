import autogen

SEED = 23491100

config_list = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": ["gpt-3.5-turbo"],
    },
)

assistants_configuration = {"config_list": config_list, "seed": SEED}


llm_config = {
    "request_timeout": 160,
    "config_list": config_list,
     "seed": 22,
    "use_cache": True,  # Use False to explore LLM non-determinism.
}

def check_termination(x):
    if "content" in x and x["content"] is not None:
        if x["content"].endswith("TERMINATE"):
            return True
    return False


user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    code_execution_config={"last_n_messages": 10, "work_dir": f"groupchat", "use_docker": False,},
    human_input_mode="NEVER",
    default_auto_reply="default_auto_reply",
    max_consecutive_auto_reply=5,
    is_termination_msg=check_termination
)



# create an AssistantAgent instance named "assistant"
# assistant = autogen.AssistantAgent(
#     name="assistant",
#     llm_config=llm_config,
#     is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
# )

assistant = autogen.AssistantAgent(
            name="assistant",
            max_consecutive_auto_reply=3, llm_config=llm_config,)



autogen.ChatCompletion.start_logging()
task1 = '''
<begin recipe>
**Recipe Name:** System design 

**Steps:**
1. Define functional and non-functional requirements.
2. Identify possible questions to ask the interviewer for more information.
3. Give the estimates for  Requests Per Second, Storage, and Bandwidth requirements assuming 1 Million DAUs.
4. Create a high-level design (HLD) with top-level components, data flow and write the mermaid code.
5. Design the Low-level design components:
   - Entity-Relationship (ER) diagram in mermaid code with detailed database schema.
   - Sample APIs with data types and major services involved.
   - Low-level design of critical services and explain core algorithms involved.
6. Identify potential single points of failure and their respective solutions.
7. Write down the above data to fk.md file
</end recipe>


Here is a new task:
Give me system design for Flipkart e-commerce system design
'''

user_proxy.initiate_chat(assistant, message=task1)