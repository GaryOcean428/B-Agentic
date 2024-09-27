# agent_config.py


class AgentConfig:
    def __init__(self, **kwargs):
        # Initialization code for agent configuration
        self.parameters = kwargs
        # Add default parameters or settings here
        self.embeddings_model = "large"  # Added attribute
        self.max_tool_response_length = 1000  # Added attribute


class AgentContext:
    _contexts = {}

    def __init__(self, config, context_id=None):
        self.config = config
        self.id = context_id or "default"
        self.paused = False
        self.log = None  # Placeholder for a logging mechanism
        # Additional initialization code
        AgentContext._contexts[self.id] = self

    @staticmethod
    def first():
        # Return the first available context
        if AgentContext._contexts:
            return next(iter(AgentContext._contexts.values()))
        return None

    @staticmethod
    def get(context_id):
        # Retrieve a context by its ID
        return AgentContext._contexts.get(context_id)

    @staticmethod
    def remove(context_id):
        # Remove a context by its ID
        if context_id in AgentContext._contexts:
            del AgentContext._contexts[context_id]

    def reset(self):
        # Reset the context to its initial state
        self.paused = False
        self.log = None
        # Add any additional reset logic here

    def communicate(self, text):
        # Handle incoming communication
        # Implement the logic for processing the user's input
        pass

    def process_result(self):
        # Process and return the result after communication
        # Implement the logic to generate and return the agent's response
        return "Processed result"

    def set_log(self, log):
        # Set the logging mechanism
        self.log = log
