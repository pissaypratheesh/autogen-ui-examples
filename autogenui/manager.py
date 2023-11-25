# a manager class that can
# load an autogen flow run an autogen flow and return the response to the client
import sys
import logging

from typing import Dict
import autogen
from .utils import parse_token_usage
import time
from autogen.agentchat.contrib.teachable_agent import TeachableAgent
from autogen import UserProxyAgent
from .lm_agent import LMStudioAgent
from .search.search_query import get_search_result
from .search.image_api import getBingImages
from .tasks.system_design import extract_tasks
from .tasks.numeric_hash import create_numeric_hash
from .tasks.refine_str import remove_whitespace_and_special_chars
from .tasks.file_operations import create_directory
from .tasks.extract_first_user_msg import get_first_user_content
from .tasks.fetch_from_memory import get_search_result_from_agent_memory

mistralAssistant = [{
    "api_type": "open_ai",
    "api_base": "http://localhost:1234/v1",
    "api_key": "NULL",
}]

class Manager(object):
    def __init__(self) -> None:
        logging.basicConfig(filename='autogen.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        pass

    def run_flow(self, prompt: str, flow: str = "default") -> None:
        #autogen.ChatCompletion.start_logging(compact=False)
        config_list = autogen.config_list_from_json(
            env_or_file="OAI_CONFIG_LIST_AZURE",
            file_location=".",
        )
        llm_config = {
            "seed": 42,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
            "use_cache": True,  # whether to use cache
        }

        assistant = autogen.AssistantAgent(
            name="assistant",
            max_consecutive_auto_reply=3, llm_config=llm_config,)

        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            llm_config=llm_config,
            max_consecutive_auto_reply=3,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": "scratch/coding",
                "use_docker": False
            },
        )
        start_time = time.time()
        user_proxy.initiate_chat(
            assistant,
            message=prompt,
        )

        messages = user_proxy.chat_messages[assistant]
        logged_history = autogen.ChatCompletion.logged_history
        logging.info('Stopping logging for run_flow method')
        response = {
            "messages": messages[1:],
            "usage": parse_token_usage(logged_history),
            "duration": time.time() - start_time,
        }
        return response    
    def run_summarization_flow(self, prompt: str, id: str = None) -> None:
        logging.info('Starting logging for run_flow method')
        config_list = autogen.config_list_from_json(
            env_or_file="OAI_CONFIG_LIST_AZURE",
            file_location=".",
        )
        llm_config = {
            "seed": 42,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
            "use_cache": True,  # whether to use cache
        }

        assistant = autogen.AssistantAgent(
            name="assistant",
            max_consecutive_auto_reply=3, llm_config=llm_config,)

        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            llm_config=llm_config,
            max_consecutive_auto_reply=3,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": "scratch/coding",
                "use_docker": False
            },
        )
        start_time = time.time()
        user_proxy.initiate_chat(
            assistant,
            message=prompt,
        )

        messages = user_proxy.chat_messages[assistant]
        logged_history = autogen.ChatCompletion.logged_history
        logging.info('Stopping logging for run_system_design_flow method')
        response = {
            "messages": messages[1:],
            "usage": parse_token_usage(logged_history),
            "duration": time.time() - start_time,
        }
        return response    
    
    def run_local_llm_flow(self, prompt: str, flow: str = "default") -> None:
        logging.info('Starting logging for run_system_design_flow method')
        promptStr = prompt.replace("/local_llm ", '')
        refined = promptStr
        seed = create_numeric_hash(refined)
        llm_config = {
            "seed": seed,  # seed for caching and reproducibility
            "config_list": mistralAssistant,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
            "use_cache": True,  # whether to use cache
        }

        assistant = LMStudioAgent(
            name="Principal Software Engineer",
            system_message="""You are a Principal Software Engineer.
                              You are designing the complete architecture for a given system.""",
            default_auto_reply="default_auto_reply",
            llm_config=llm_config)
        

        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            llm_config=llm_config,
            max_consecutive_auto_reply=3,
            default_auto_reply="default_auto_reply",
            system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
                             Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "last_n_messages": 10,
                "work_dir": "local_llm",
                "use_docker": False
            },
        )
        start_time = time.time()
        user_proxy.initiate_chat(
            assistant,
            message=refined, 
            clear_history=True
        )
        logged_history = autogen.ChatCompletion.logged_history
        autogen.ChatCompletion.stop_logging()
        response = {
            "messages": user_proxy.chat_messages[assistant],
            "usage": parse_token_usage(logged_history),
            "duration": time.time() - start_time,
        }
        return response
    

    def run_teachable_agent_flow(self, prompt: str, flow: str = "default") -> None:
        refined = "teachable/"
        create_directory(f"{refined}")
        autogen.ChatCompletion.start_logging(compact=False)
        start_time = time.time()
        
        numeric_hash = create_numeric_hash(prompt)
        config_list = autogen.config_list_from_json(
            env_or_file="OAI_CONFIG_LIST",
            file_location=".",
        )
        llm_config = {
            "seed": numeric_hash,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            
            "temperature": 0,  # temperature for sampling
            "use_cache": True,  # whether to use cache
        }
        #Create a teachable agent config
        teach_config={
            "verbosity": 0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
            "reset_db": False,  # Set to True to start over with an empty database.
            "path_to_db_dir": "./tmp/notebook/teachable_agent_db",  # Path to the directory where the database will be stored.
            "recall_threshold": 1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
        }
        user = UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
            max_consecutive_auto_reply=1,
        )

        # user_proxy = autogen.UserProxyAgent(
        #     name="user_proxy",
        #     human_input_mode="NEVER",
        #     llm_config=llm_config,
        #     max_consecutive_auto_reply=3,
        #     is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        #     code_execution_config={
        #         "work_dir": f"{refined}",
        #         "use_docker": False
        #     },
        # )

        teachable_agent = TeachableAgent(
            name="teachableagent",
            llm_config=llm_config,
            max_consecutive_auto_reply=1,
            teach_config=teach_config)
        
        #Train the teachable agent by user feedbacks
        teachable_agent.learn_from_user_feedback()

        #initiate
        user.initiate_chat(teachable_agent, message=f"{prompt.replace('/teachable', '')}", clear_history=False)
        logged_history = autogen.ChatCompletion.logged_history
        autogen.ChatCompletion.stop_logging()
        response = {
            "messages": user.chat_messages[teachable_agent][1:],
            "usage": parse_token_usage(logged_history),
            "duration": time.time() - start_time,
        }
        return response
    
    def run_system_design_flow(self, prompt: str, flow: str = "default") -> None:
        company = prompt.replace("/system_design", '')
        refined = remove_whitespace_and_special_chars(company)
        refined = "system_design/" + refined[:10]
        create_directory(f"{refined}")

        autogen.ChatCompletion.start_logging(compact=False)

        config_list = autogen.config_list_from_json(
            env_or_file="OAI_CONFIG_LIST",
            file_location=".",
        )
        numeric_hash = create_numeric_hash(prompt)
        llm_config = {
            "seed": numeric_hash,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
            "use_cache": True,  # whether to use cache
        }

        assistant = autogen.AssistantAgent(
            name="assistant",
            max_consecutive_auto_reply=3, llm_config=llm_config,)

        # create a UserProxyAgent instance named "user_proxy"
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            llm_config=llm_config,
            max_consecutive_auto_reply=3,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": f"{refined}",
                "use_docker": False
            },
        )

        #Create a teachable agent config
        teach_config={
            "verbosity": 0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
            "reset_db": True,  # Set to True to start over with an empty database.
            "path_to_db_dir": "./tmp/notebook/teachable_agent_db",  # Path to the directory where the database will be stored.
            "recall_threshold": 1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
        }

        teachable_agent = TeachableAgent(
            name="teachableagent",
            llm_config=llm_config,
            max_consecutive_auto_reply=1,
            teach_config=teach_config)
        
        #Train the teachable agent by user feedbacks
        teachable_agent.learn_from_user_feedback()

        query = f"""what does the company {company} do? give me all its features and services that it provides in bullet points"""
        search_res = get_search_result(query)

        systemDesign = []


        # Save the original stdout
        original_stdout = sys.stdout
        # Open a file in write mode
        with open(f"{refined}/systemDesign.md", "w") as file:
            # Redirect stdout to the file
            sys.stdout = file
            user_proxy.initiate_chat(teachable_agent, message=f"Remember this: {search_res}", clear_history=True)

            #Fetch from memory and store in systemDesign array
            mem_query = f"Tell me about: {company}"
            user_proxy.initiate_chat(teachable_agent, message=f'{mem_query}', clear_history=True)
            systemDesign.append(get_first_user_content(user_proxy.chat_messages[teachable_agent][1:]))


            start_time = time.time()
            user_proxy.initiate_chat(
                assistant,
                clear_history=True,
                message=f'''
                    Assume you are building a system design for a company, give functional and non-functional requirements
                    and brainstorm on all possible stuffs to keep in mind (highlight main ones) and
                    also write the content in a markdown file by name {company}_functions.md. Question: {company}''',
            )
            systemDesign.append(get_first_user_content(user_proxy.chat_messages[assistant][1:]))


            user_proxy.initiate_chat(
                assistant,
                message=f'''
                    For the same, give me the Requests Per Second, storage, bandwidth requirements assuming 1 billion DAUs with explanation,
                    and also write the content in a markdown file by name {company}_calc.md''',
            )
            systemDesign.append(get_first_user_content(user_proxy.chat_messages[assistant][1:]))
            

            
            user_proxy.initiate_chat(
                assistant,
                message=f'''
                    For the same, give a simple intro of the top-level HLD with detailed data flow using the latest technologies with Mermaid code
                    and also write the content in a markdown file by name {company}_hld.md''',
            )
            systemDesign.append(get_first_user_content(user_proxy.chat_messages[assistant][1:]))
            
            

            user_proxy.initiate_chat(
                assistant,
                message=f'''
                    For the same, create an Entity-Relationship (ER) diagram with detailed DB schema with relationships,
                    sample APIs (with data types) and major services
                    and also write the content in a markdown file by name {company}_lld.md''',
            )
            systemDesign.append(get_first_user_content(user_proxy.chat_messages[assistant][1:]))
            
            
            
            user_proxy.initiate_chat(
                assistant,
                message=f'''
                    For the same, explain the low-level design of critical services involved and possible algorithms
                    and also write the content in a markdown file by name {company}_algos.md''',
            )
            systemDesign.append(get_first_user_content(user_proxy.chat_messages[assistant][1:]))
            
            

            user_proxy.initiate_chat(
                assistant,
                message=f'''Reflect on the sequence and create a recipe containing all the above steps necessary and name it.''',
            )
            systemDesign.append(get_first_user_content(user_proxy.chat_messages[assistant][1:]))
            

        # Reset stdout to its original value
        sys.stdout = original_stdout
        systemDesign.append({
                "content": f"Brief from search result: {search_res}",
                "role": "user"
        })
        logged_history = autogen.ChatCompletion.logged_history
        autogen.ChatCompletion.stop_logging()
        response = {
            "messages": systemDesign,
            "usage": parse_token_usage(logged_history),
            "duration": time.time() - start_time,
        }
        return response
    



