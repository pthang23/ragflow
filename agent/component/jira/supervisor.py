import logging
import json
import pandas as pd
from abc import ABC
from api.db import LLMType
from api.db.services.llm_service import LLMBundle
from agent.component import GenerateParam, Generate

COMPONENTS_DESCRIPTION = dict()
with open('components_description.json', 'r', encoding='utf-8') as fr:
    COMPONENTS_DESCRIPTION = json.load()


class JiraSupervisorParam(GenerateParam):
    """
    Define the JiraSupervisor component parameters.
    """

    def __init__(self):
        super().__init__()
        self.jira_components = [
            "GetAPIs", "Retract", "Generate", "Retrieval",
            "APIGetAllTicket", "APICreateTicket", "APIDeleteTicket", "APIUpdateTicket",
            "APICreateComment", "APIDeleteComment"
        ]
        self.prompt = ""

    def check(self):
        super().check()
        self.check_valid_value(
            self.jira_components, "Jira Components",
            [
                "GetAPIs", "Generate", "Retrieval",
                "APIGetAllTicket", "APICreateTicket", "APIDeleteTicket", "APIUpdateTicket",
                "APICreateComment", "APIDeleteComment"
            ]
        )

    def get_prompt(self):
        components_description = {}

        prompt_components_description = ""
        for component in components_description:
            if component in self.jira_components:
                prompt_components_description += f"- {component}: \n"
                descriptions = components_description[component]
                for description in descriptions:
                    prompt_components_description += f"\t+ {description}: {descriptions[description] if descriptions[description] else 'nothing'} \n"

        self.prompt = f"""
Role: You're a professional agent supervisor for Jira, responsible for overseeing multiple specialized Jira agents and ensuring they collaborate seamlessly to provide accurate, efficient responses to user query
Agents Description:
{prompt_components_description}
Chain of Thought:
    - Analyse Input & Define Workflow:
    - Confirm & Optimize Workflow:
Requirement:
User Query:
"""
        return self.prompt


class JiraSupervisor(Generate, ABC):
    component_name = "JiraSupervisor"

    def _run(self, history, **kwargs):
        query = self.get_input()
        query = str(query["content"][0]) if "content" in query else ""

        chat_mdl = LLMBundle(self._canvas.get_tenant_id(), LLMType.CHAT, self._param.llm_id)
        dsl = chat_mdl.chat(self._param.get_prompt(), [{"role": "user", "content": query}],
                            self._param.gen_conf())

        # Update Canvas dsl
        pass

        logging.debug(f"dsl: {dsl}")
        return JiraSupervisor.be_output(dsl)