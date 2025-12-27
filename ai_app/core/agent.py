# генерация рецепта по заданным ингредиентам
# поиск рецепта в интернете
# генерация похожего рецепта

from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
import os, inspect
from app.core.utils.get_prompt  import get_prompt
from app.core.utils.state import AgentState
from app.core.utils.recipe_model import Recipe
from typing import Literal
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()



class BuReAgent:
    def __init__(self):
        try:
            self.llm = ChatMistralAI(
                api_key=os.getenv("MISTRAL_API_KEY"),
                model=os.getenv("LLM_MODEL"),
                temperature=0.1
            )
        except Exception as e:
            print(f"Ошибка инициализации LLM: {e}")
            raise
        self.tavily = TavilySearch(
            api_key=os.getenv("TAVILY_API_KEY"), 
            max_results=1,
            include_answer=True
        )
        self.parser = PydanticOutputParser(pydantic_object=Recipe)
        self.agent = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("classify", self._classify)
        workflow.add_node("generate_recipe", self._generate_recipe_with_ingredients)
        workflow.add_node("search_recipe", self._search_for_recipe)
        

        workflow.add_edge(START, "classify")
        workflow.add_conditional_edges("classify", self._routing_func, 
                                       {
                                           "generate" : "generate_recipe",
                                           "search" : "search_recipe"
                                       })
        workflow.add_edge("generate_recipe", END)
        workflow.add_edge("search_recipe", END)
        return workflow.compile()

    def _generate_recipe_with_ingredients(self, state : AgentState) -> AgentState:
        """
        Этот инструмент генерирует список рецептов на основе списка заданных ингредиентов.
        """
        prompt = get_prompt(inspect.currentframe().f_code.co_name.lstrip('_'))
        system_prompt = PromptTemplate(
            template=prompt + "\nЗапрос пользователя:\n{query}\nФормат вывода: {format_instructions}",
            input_variables=["query"],
            partial_variables={ "format_instructions": self.parser.get_format_instructions()}
        )
        chain = system_prompt | self.llm | self.parser
        result = chain.invoke({"query" :  state.get("user_query")})
        state["messages"].append(AIMessage(content="Сгенерирован рецепт из предложенного списка ингредиентов"))
        state["generated_recipe"] = result
        print("=========RESULT IN GENERATE RECIPE==========")
        print(result)
        return state
    
    def _search_for_recipe(self, state : AgentState) -> AgentState:
        """
        Этот инструмент ищет в интернете заданный ему рецепт. 
        """
        tavily_res = self.tavily.invoke({"query" : state.get("user_query")})
        system_template = get_prompt(inspect.currentframe().f_code.co_name.lstrip('_'))
        prompt_template = PromptTemplate(
            template=system_template + "\n Запрос пользователя:\n{query}\n Результаты поиска:\n {search_results}\n Формат вывода:\n {format_instructions}",
            input_variables=["query", "search_results"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )
        chain = prompt_template | self.llm | self.parser
        recipe = chain.invoke({"query": state["user_query"], "search_results": tavily_res.get("answer", None)})
        state["messages"].append(AIMessage(content="Найден рецепт в интернете"))
        state["searched_recipe"] = recipe
        print("=========STATE IN SEARCH RECIPE==========")
        print(state)
        return state
    
    def _classify(self, state : AgentState) -> AgentState:
        """Выбирает нужный инструмент"""
        prompt = get_prompt(inspect.currentframe().f_code.co_name.lstrip('_'))
        classify_prompt = PromptTemplate(
            template=prompt + "\n Запрос пользователя: {user_query}",
            input_variables=["user_query"]
        )
        chain = classify_prompt | self.llm | StrOutputParser()
        result = chain.invoke({"user_query": state["user_query"]})
        state["tool"] = result
        return state
    
    def _routing_func(self, state: AgentState) -> Literal["generate", "search"]:
        if state["tool"] == "generate":
            return "generate"
        elif state["tool"] == "search":
            return "search" 
        else:
            raise ValueError(f"Invalid tool: {state["tool"]}")
    
    def invoke(self, query : str):
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_query" : query, 
            "generated_recipe" : None, 
            "searched_recipe" : None, 
            "tool" : None
        }
        try:
            result = self.agent.invoke(initial_state)
            generated = result.get("generated_recipe", None)  # Обратите внимание на множественное число
            searched = result.get("searched_recipe", None)

            # Проверяем и возвращаем первый найденный
            if generated:
                return generated
            elif searched:
                return searched
            else:
                return None
        except Exception as e:
            print(f"Ошибка при вызове agent.invoke: {e}")  
            return None

    

#agent = BuReAgent()
#queue = "я хочу приготовить что-то типы пасты болоньезе, но без томатной пасты"
#recipe = agent.invoke(queue)

#recipe_json = recipe.model_dump_json()
#print(recipe_json)
#print(type(recipe_json))