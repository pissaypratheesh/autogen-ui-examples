
import sys
from typing import Optional, List, Dict, Any, Tuple, Union, Callable

import autogen
from autogen import AssistantAgent, Agent, GroupChatManager, GroupChat, ConversableAgent


def clean_message(message: Dict) -> Dict:
    if message["role"] == "function":
        message["role"] = "assistant"
    return message


def filter_incompatible_message(message: Dict) -> bool:
    if message["role"] not in ["user", "assistant", "system"]:
        return False
    if message["content"] is None:
        return False
    if message["content"] == "":
        return False
    return True


def make_lmstudio_compatible(messages: List[Dict]) -> List[Dict]:
    filtered_messages = list(filter(filter_incompatible_message, map(clean_message, messages)))
    return filtered_messages


class LMStudioAgent(AssistantAgent):

    def __init__(self, name: str, system_message: Optional[str] = AssistantAgent.DEFAULT_SYSTEM_MESSAGE,
                 llm_config: Optional[Union[Dict, bool]] = None,
                 is_termination_msg: Optional[Callable[[Dict], bool]] = None,
                 max_consecutive_auto_reply: Optional[int] = None, human_input_mode: Optional[str] = "NEVER",
                 code_execution_config: Optional[Union[Dict, bool]] = False, **kwargs):

        super().__init__(name, system_message, llm_config, is_termination_msg, max_consecutive_auto_reply,
                         human_input_mode, code_execution_config, **kwargs)
        for function_call in self._reply_func_list:
            if function_call["reply_func"] == ConversableAgent.generate_oai_reply:
                function_call["reply_func"] = LMStudioAgent.generate_oai_reply


    def generate_oai_reply(self, messages: Optional[List[Dict]] = None, sender: Optional[Agent] = None,
                              config: Optional[Any] = None) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using autogen.oai."""
        llm_config = self.llm_config if config is None else config
        if llm_config is False:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        filtered_messages = make_lmstudio_compatible(messages)
        # TODO: #1143 handle token limit exceeded error
        response = autogen.oai.ChatCompletion.create(
            context=messages[-1].pop("context", None), messages=self._oai_system_message + filtered_messages,
            **llm_config
        )
        return True, autogen.oai.ChatCompletion.extract_text_or_function_call(response)[0]


class LMStudioChatManager(GroupChatManager):

    def __init__(self, groupchat: GroupChat, name: Optional[str] = "chat_manager",
                 max_consecutive_auto_reply: Optional[int] = sys.maxsize, human_input_mode: Optional[str] = "NEVER",
                 system_message: Optional[str] = "Group chat manager.", **kwargs):

        super().__init__(groupchat, name, max_consecutive_auto_reply, human_input_mode, system_message, **kwargs)
        for function_call in self._reply_func_list:
            if function_call["reply_func"] == ConversableAgent.generate_oai_reply:
                function_call["reply_func"] = LMStudioChatManager.generate_oai_reply

    def generate_oai_reply(self, messages: Optional[List[Dict]] = None, sender: Optional[Agent] = None,
                              config: Optional[Any] = None) -> Tuple[bool, Union[str, Dict, None]]:

        """Generate a reply using autogen.oai."""
        llm_config = self.llm_config if config is None else config
        if llm_config is False:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        filtered_messages = make_lmstudio_compatible(messages)
        # TODO: #1143 handle token limit exceeded error
        response = autogen.oai.ChatCompletion.create(
            context=messages[-1].pop("context", None), messages=self._oai_system_message + filtered_messages,
            **llm_config
        )
        return True, autogen.oai.ChatCompletion.extract_text_or_function_call(response)[0]
