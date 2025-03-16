import os
from dotenv import load_dotenv
import uuid
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from vectorstorecreation import load_vector_store
from better_profanity import profanity
from templates import template_details
from logger import logger
#Load the vector store once at startup (global variable)
vector_store=load_vector_store()
retriever=vector_store.as_retriever(search_kwargs={"k":3})


class ChatModelPortfolio():
    def __init__(self):
        load_dotenv()
        GROQ_API_KEY=os.getenv("GROC_LLM_API")
        vector_store=load_vector_store()
        profanity.add_censor_words(['adult'])
        self.history_store = {} # In-memory history store
        self.llm=ChatGroq(api_key=GROQ_API_KEY,max_tokens=400)
        self.retriever=vector_store.as_retriever(search_kwargs={"k":3})
        self.prompt=PromptTemplate(
            input_variables=["history", "input", "context"],
            template= template_details)
        
        
    def generate_session_id(self):
        """Generate session id for the session
            Returns:  (UUID)session id
        """
        session_id=str(uuid.uuid4())
        return session_id
    
    def get_session_history(self,session_id: str) -> ChatMessageHistory:
        try:
            if session_id not in self.history_store:
                self.history_store[session_id] = ChatMessageHistory()
            return self.history_store[session_id]
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

            rag_chain_with_history = RunnableWithMessageHistory(
                runnable=(
                    {"context": lambda x: retriever.invoke(x["input"]), "input": RunnablePassthrough(), "history": lambda x: x.get("history", "")}
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
            return response
        except Exception as e:
            logger.error(f"Error generating response ---{e}")
            return "Sorry, we are having trouble generating reponse, please try again, later"
        