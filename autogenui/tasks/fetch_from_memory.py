def get_search_result_from_agent_memory(search_term, teachable_agent, user):
    user.initiate_chat(teachable_agent, message=f"Tell me about: {search_term}", clear_history=False)
    return user.last_message()