import os
from dotenv import load_dotenv
import uuid
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from upstash_redis import Redis
from vectorstoreloader import load_vector_store
from better_profanity import profanity
from templates import template_details
from logger import logger


class ChatModelPortfolio():
    def __init__(self):
        load_dotenv()
        GROQ_API_KEY=os.getenv("GROC_LLM_API")
        vector_store=load_vector_store()
        profanity.add_censor_words(['adult'])
        self.history_store = {} # In-memory history store
        self.llm=ChatGroq(model=os.getenv("LLM_MODEL"),api_key=GROQ_API_KEY,max_tokens=400)
        self.retriever=vector_store.as_retriever(search_kwargs={"k":3})
        self.prompt=PromptTemplate(
            input_variables=["history", "input", "context"],
            template= template_details)
        self.redis = Redis(
            url=os.getenv("UPSTASH_REDIS_REST_URL"),
            token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
        )
        
    def generate_session_id(self):
        """Generate session id for the session
            Returns:  (UUID)session id
        """
        session_id=str(uuid.uuid4())
        return session_id
    
    def get_session_history(self,session_id: str) -> ChatMessageHistory:
        try:
            # Use Upstash Redis to store/retrieve history as a list
            history_key = f"chat_history:{session_id}"
            messages = self.redis.lrange(history_key, -5, -1)  # Get last 5 messages (returns list of strings)
            chat_history = ChatMessageHistory()
            for msg in messages:
                # Messages are stored as "role:content" (e.g., "human:hello")
                role, content = msg.split(":", 1)  # Split directly on string
                if role == "human":
                    chat_history.add_user_message(content)
                elif role == "ai":
                    chat_history.add_ai_message(content)
            return chat_history
        except Exception as e:
            logger.error(f"Error getting session history ---{e}")
            return ChatMessageHistory()
    
    def filter_input(self, message: str) -> bool: # Handle inappropriate. 

        return profanity.contains_profanity(message)
    
    def ChatHandler(self,message,session_id)->RunnableWithMessageHistory:
        # Define the ChatHandler function here. It should return a RunnableWithMessageHistory object.
        if self.filter_input(message):
            return "Sorry, I’m here to help with portfolio-related questions only."
        try:
            chat_deletion_time=os.getenv("CHAT_DELETION_TIME") or 600
            history_key = f"chat_history:{session_id}"
            self.redis.rpush(history_key, f"human:{message}")
            self.redis.expire(history_key, chat_deletion_time) # Set TTL to remove chat from redis cache
            rag_chain_with_history = RunnableWithMessageHistory(
                runnable=(
                    {"context": lambda x: self.retriever.invoke(x["input"]), "input": RunnablePassthrough(), "history": lambda x: x.get("history", "")}
                    | self.prompt
                    | self.llm
                    | StrOutputParser()
                            ),
                get_session_history=self.get_session_history,
                input_messages_key="input",  
                history_messages_key="history"
            )

            response=rag_chain_with_history.invoke(
                    {"input": message},
                    config={"configurable": {"session_id": session_id}}
                )
            # Store AI response in Redis
            self.redis.rpush(history_key, f"ai:{response}")
            self.redis.expire(history_key, chat_deletion_time)  # Set TTL to remove chat from redis cache
            
            return response
        except Exception as e:
            logger.error(f"Error generating response ---{e}")
            return "Sorry, we are having trouble generating reponse, please try again, later"
        