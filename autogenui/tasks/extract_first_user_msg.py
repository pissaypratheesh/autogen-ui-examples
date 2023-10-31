from collections import defaultdict

def get_first_user_content(data,key="user"):
    if data and data[0].get('role') == key:
        first_user_content = data[0]#.get('content')
        return first_user_content
    else:
        return []

# Example usage:
# data = [
#     {'content': 'This is user content.', 'role': 'user'},
#     {'content': 'This is assistant content.', 'role': 'assistant'},
#     {'content': 'Another user message.', 'role': 'user'},
#     {'content': 'Another assistant response.', 'role': 'assistant'},
# ]

# result = get_first_user_content(data)
# print(result)


