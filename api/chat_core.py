import os, redis
from dotenv import load_dotenv

from langchain_redis import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory

# new imports for prompt
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

from langchain_ollama import ChatOllama
from langchain.chains import ConversationChain

load_dotenv()
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

def make_chain(session_id: str) -> ConversationChain:

    history = RedisChatMessageHistory(
        session_id=session_id,
        redis_client=redis_client,
    )
    memory = ConversationBufferMemory(
        chat_memory=history,
        return_messages=True,
    )

    # --- updated prompt construction ---
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a Chatbot!"
        ),
        # this pulls in the entire past conversation
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ])
    # ---------------------------------------

    llm = ChatOllama(model="gemma3:4b", temperature=0.7)
    return ConversationChain(llm=llm, prompt=prompt, memory=memory)