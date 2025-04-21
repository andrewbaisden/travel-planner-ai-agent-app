import logging
import json
from typing import Dict, List, Any

from tools import (
    location_identifier,
    travel_info_searcher,
    travel_plan_generator,
    reflect_on_plan,
    improve_travel_plan
)


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TravelAgent:

    def __init__(self, ollama_agent, model_name="llama3"):

        self.model_name = model_name
        self.ollama_agent = ollama_agent
        self.memory = {}

    def plan(self, user_query):

        logger.info("Starting planning phase...")

        destinations = location_identifier(self.ollama_agent, user_query)

        self.memory["user_query"] = user_query
        self.memory["destinations"] = destinations

        plan_result = {
            "destinations": destinations,
            "user_query": user_query
        }

        logger.info(
            f"Planning phase complete. Identified {len(destinations)} destinations.")
        return plan_result

    def research(self):

        logger.info("Starting research phase...")

        destinations = self.memory.get("destinations", [])
        if not destinations:
            logger.warning(
                "No destinations to research. Planning phase may have failed.")
            return {}

        research_results = {}

        for destination in destinations:
            logger.info(f"Researching destination: {destination}")

            info = travel_info_searcher(self.ollama_agent, destination)
            research_results[destination] = info

        self.memory["research"] = research_results

        logger.info(
            f"Research phase complete. Gathered information for {len(research_results)} destinations.")
        return research_results

    def generate(self):

        logger.info("Starting generation phase...")

        user_query = self.memory.get("user_query", "")
        destinations = self.memory.get("destinations", [])
        research = self.memory.get("research", {})

        if not destinations or not research:
            logger.warning(
                "Missing destinations or research data. Previous phases may have failed.")
            return "# Travel Plan\n\nInsufficient information to generate a complete travel plan."

        travel_plan = travel_plan_generator(
            self.ollama_agent,
            user_query,
            destinations,
            research
        )

        self.memory["travel_plan"] = travel_plan

        logger.info("Generation phase complete.")
        return travel_plan

    def reflect(self):

        logger.info("Starting reflection phase...")

        user_query = self.memory.get("user_query", "")
        travel_plan = self.memory.get("travel_plan", "")

        if not travel_plan:
            logger.warning(
                "No travel plan to reflect on. Generation phase may have failed.")
            return {}

        reflection_data = reflect_on_plan(
            self.ollama_agent,
            travel_plan,
            user_query
        )

        self.memory["reflection"] = reflection_data

        logger.info("Reflection phase complete.")
        return reflection_data

    def improve(self):

        logger.info("Starting improvement phase...")

        user_query = self.memory.get("user_query", "")
        travel_plan = self.memory.get("travel_plan", "")
        reflection_data = self.memory.get("reflection", {})

        if not travel_plan or not reflection_data:
            logger.warning(
                "Missing travel plan or reflection data. Previous phases may have failed.")
            return travel_plan or "# Travel Plan\n\nInsufficient information to generate a complete travel plan."

        if not reflection_data.get('issues') and not reflection_data.get('missing_info'):
            logger.info("No improvements needed.")
            return travel_plan

        improved_plan = improve_travel_plan(
            self.ollama_agent,
            travel_plan,
            user_query,
            reflection_data
        )

        self.memory["improved_plan"] = improved_plan

        logger.info("Improvement phase complete.")
        return improved_plan

    def run_workflow(self, user_query):

        logger.info(f"Starting agentic workflow for query: {user_query}")

        self.memory = {}

        plan_result = self.plan(user_query)
        research_result = self.research()
        initial_plan = self.generate()
        reflection_result = self.reflect()
        final_plan = self.improve()

        workflow_results = {
            "plan": plan_result,
            "research": research_result,
            "initial_plan": initial_plan,
            "reflection": reflection_result,
            "final_plan": final_plan
        }

        logger.info("Agentic workflow complete.")
        return workflow_results
