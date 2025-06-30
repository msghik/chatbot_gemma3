import os, redis
from dotenv import load_dotenv

from langchain_redis import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory

# Import for the new prompt structure
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

# Import ChatOpenAI to connect to the LM Studio endpoint
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

load_dotenv()
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

def make_chain(session_id: str) -> ConversationChain:
    """
    Creates a LangChain ConversationChain configured to use an LM Studio model,
    with conversation history stored in Redis.

    Args:
        session_id: A unique identifier for the conversation session.

    Returns:
        An initialized ConversationChain.
    """
    print(f'\n This is Session_id: {session_id}\n')

    # Set up Redis-backed chat message history
    history = RedisChatMessageHistory(
        session_id=session_id,
        redis_client=redis_client,
    )
    
    print(f'\n This is History: {history}\n')

    # Set up conversation memory
    memory = ConversationBufferMemory(
        chat_memory=history,
        return_messages=True,
    )

    print(f'\n This is Memory: {memory}\n')

    # Define the chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a Chatbot!"
        ),
        # This placeholder will be filled by the conversation history
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ])

    # --- LM Studio Integration ---
    # Instantiate the ChatOpenAI class to connect to your LM Studio server.
    # By default, LM Studio runs on port 1234.
    llm = ChatOpenAI(
        # The model parameter is not strictly required if you have only one model loaded in LM Studio,
        # but it's good practice. You can often find the model identifier in LM Studio's UI.
        model="google/gemma-3-4b", 
        temperature=0.7,
        # Point the base_url to your LM Studio server's IP address and port.
        # Remember to include the /v1 suffix.
        base_url="http://192.168.120.138:1234/v1",
        # LM Studio does not require an API key, so a placeholder is sufficient.
        api_key="not-needed"
    )
    # ---------------------------

    return ConversationChain(llm=llm, prompt=prompt, memory=memory)