import os
from dotenv import load_dotenv
import uuid
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough,RunnableSequence,RunnableBranch,RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from upstash_redis import Redis
from vectorstoreloader import load_vector_store
from better_profanity import profanity
from templates import template_details,template_for_chat_classfication
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from logger import logger

class ChatMessageClassification(BaseModel):
    """Classifies user messages into predefined categories"""

    Greeting: bool = Field(
        default=False,
        description="True if the user message is a greeting or conversation starter, else False"
    )
    PortfolioQuestion: bool = Field(
        default=False,
        description="True if the user message is about portfolio-related questions, else False"
    )
    Unknown: bool = Field(
        default=False,
        description="True if the user message is neither a greeting nor a portfolio-related question, else False"
    )
    Contact: bool = Field(
        default=False,
        description="True if the user message is about providing contact information, else False"
    )
load_dotenv()
GROQ_API_KEY=os.getenv("GROC_LLM_API")
vector_store=load_vector_store()
profanity.add_censor_words(['adult'])
llm=ChatGroq(model=os.getenv("LLM_MODEL"),api_key=GROQ_API_KEY,max_tokens=400)
structured_llm=llm.with_structured_output(ChatMessageClassification)
retriever=vector_store.as_retriever(search_kwargs={"k":2})
classfication_prompt=PromptTemplate.from_template(template_for_chat_classfication)
prompt=PromptTemplate(input_variables=["history", "input", "context"],template=template_details)

class ChatModelPortfolio():
    def __init__(self):
        self.redis = Redis(
            url=os.getenv("UPSTASH_REDIS_REST_URL"),
            token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
        )
        self.chat_deletion_time = os.getenv("CHAT_DELETION_TIME") or 600
        
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
            messages = self.redis.lrange(history_key, -3, -1)  # Get last 3 messages (returns list of strings)
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
        """Filter input to don't reply on inappropriate messages"""
        return profanity.contains_profanity(message)
    def greetings_msg(self) -> str:
        return f"Hi! It's nice to meet you. I'm here to help you explore my portfolio. What would you like to know about my skills, experience, or projects?"
    def contact_info(self) -> str:
        return """You can reach out to me at sk0551460@gmail.com or shivam.hireme@gmail.com or via Phone at 9815544235
          for questions, suggestions, or support. Additionally, you can stay connected with me on LinkedIn at
           https://www.linkedin.com/in/shivam-hireme/
          """
    def classfied_value_getter(self,response):
        # Convert to dictionary
        classification_dict = response.model_dump()
        # Find the category with True value
        detected_category = [key for key, value in classification_dict.items() if value]
        if detected_category:
            return detected_category[0]
        return "Unknown"  # Fallback to Unknown if no True value is found
    def rag_message_history(self, session_id: str, message: str) -> str:
        """Helper method to invoke the RAG chain with message history."""
        rag_chain_with_history = RunnableWithMessageHistory(
            runnable=RunnableSequence(
                {
                    "context": lambda x: retriever.invoke(x["input"]),
                    "input": RunnablePassthrough(),
                    "history": lambda x: x.get("history", "")
                },
                prompt,
                llm,
                StrOutputParser()
                                ),
                get_session_history=self.get_session_history,
                input_messages_key="input",
                history_messages_key="history"
                )
        return rag_chain_with_history.invoke(
            {"input": message},
        config={"configurable": {"session_id": session_id}}
        )
    
    def ChatHandler(self,message,session_id)->RunnableWithMessageHistory:
        # Define the ChatHandler function here. It should return a RunnableWithMessageHistory object.
        if self.filter_input(message):
            return "Sorry, I’m here to help with portfolio-related questions only."
        try:
            history_key = f"chat_history:{session_id}"
            self.redis.rpush(history_key, f"human:{message}")
            self.redis.expire(history_key, self.chat_deletion_time) # Set TTL to remove chat from redis cache
            
            # Classification chain
            classification_chain = RunnableSequence(
                classfication_prompt,
                structured_llm,
                self.classfied_value_getter
            )
            category = classification_chain.invoke(message)  

            branch = RunnableBranch(
                (lambda x: x == "Greeting", RunnableLambda(lambda _: self.greetings_msg())),
                (lambda x: x == "PortfolioQuestion", RunnableLambda(lambda _: self.rag_message_history(session_id, message))),
                (lambda x: x == "Contact", RunnableLambda(lambda _: self.contact_info())),
                RunnableLambda(lambda _: "Sorry, I’m here to help with portfolio-related questions only.")
            )
            response = branch.invoke(category)
            # Store AI response in Redis
            self.redis.rpush(history_key, f"ai:{response}")
            self.redis.expire(history_key, self.chat_deletion_time)  # Set TTL to remove chat from redis cache
            
            return response
        except Exception as e:
            logger.error(f"Error generating response ---{e}")
            return "Sorry, we are having trouble generating reponse, please try again, later"
        