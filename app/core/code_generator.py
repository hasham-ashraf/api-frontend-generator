from typing import Dict, List, Tuple
from langgraph.graph import Graph
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import json

class CodeGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
        
    def create_component_prompt(self, name: str, description: str, framework: str) -> str:
        return f"""Create a {framework} component named {name}.
        Description: {description}
        
        Please provide:
        1. The complete component code
        2. Any necessary imports
        3. Basic styling if needed
        
        Return the response as valid JSON with the following structure:
        {{
            "code": "component code here",
            "imports": ["import statements here"],
            "styles": "CSS/styling code here"
        }}
        """

    def generate_component(self, name: str, description: str, framework: str) -> Dict:
        messages = [
            SystemMessage(content="You are an expert frontend developer."),
            HumanMessage(content=self.create_component_prompt(name, description, framework))
        ]
        
        response = self.llm.invoke(messages)
        try:
            return json.loads(response.content)
        except:
            return {
                "code": response.content,
                "imports": [],
                "styles": ""
            }

    def analyze_requirements(self, prompt: str) -> List[Dict]:
        messages = [
            SystemMessage(content="You are a frontend architect. Analyze the requirements and break them down into components."),
            HumanMessage(content=f"""
            Analyze the following requirements and break them down into components:
            {prompt}
            
            Return the response as valid JSON with the following structure:
            {{
                "components": [
                    {{
                        "name": "component name",
                        "description": "component description",
                        "type": "component type (page/component/layout)"
                    }}
                ]
            }}
            """)
        ]
        
        response = self.llm.invoke(messages)
        try:
            return json.loads(response.content)["components"]
        except:
            return [{"name": "MainComponent", "description": prompt, "type": "component"}]

def create_generation_workflow():
    generator = CodeGenerator()
    
    def analyze(state):
        components = generator.analyze_requirements(state["prompt"])
        return {"components": components}
    
    def generate_components(state):
        generated = []
        for comp in state["components"]:
            result = generator.generate_component(
                comp["name"],
                comp["description"],
                state["framework"]
            )
            generated.append({
                "name": comp["name"],
                "code": result["code"],
                "imports": result.get("imports", []),
                "styles": result.get("styles", ""),
                "type": comp["type"]
            })
        return {"generated_components": generated}
    
    workflow = Graph()
    
    # Add nodes
    workflow.add_node("analyze", analyze)
    workflow.add_node("generate", generate_components)
    
    # Add edges
    workflow.add_edge("analyze", "generate")
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    return workflow.compile() 