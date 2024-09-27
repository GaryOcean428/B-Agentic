# python/helpers/tool.py


# Define the Tool class
class Tool:
    """
    Represents a tool that can be used by the assistant.
    """

    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func


# Define the Response class
class Response:
    """
    Represents a response from using a tool.
    """

    def __init__(self, message=None, break_loop=False):
        self.message = message
        self.break_loop = break_loop


def format_message(text, human=True):
    """
    Formats the message based on whether it's from a human or the assistant.
    """
    if human:
        return f"User: {text}"
    else:
        return f"Assistant: {text}"


# Rest of the code continues...
