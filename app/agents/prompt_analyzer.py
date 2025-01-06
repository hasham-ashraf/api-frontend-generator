from typing import List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

class PromptAnalyzer:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-sonnet-20240229")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a React application requirements analyzer. 
                Extract key features and requirements from the user's prompt.
                Return each requirement on a new line.
                Focus on functional requirements and technical specifications."""),
            ("user", "{prompt}")
        ])

    def analyze(self, prompt: str) -> List[str]:
        chain = self.prompt | self.llm
        result = chain.invoke({"prompt": prompt})
        requirements = result.content.split("\n")
        return [req.strip() for req in requirements if req.strip()]

def prompt_analyzer(state: dict) -> dict:
    analyzer = PromptAnalyzer()
    requirements = analyzer.analyze(state["prompt"])
    new_state = {
        **state,
        "requirements": requirements,
        "components": state.get("components", []),
        "files": state.get("files", {}),
        "current_stage": "architecture"
    }
    return new_state 