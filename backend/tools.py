from typing import Dict, List, Any
import logging
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def location_identifier(agent, user_preferences: str) -> List[str]:

    prompt = f"""
    Based on these travel preferences: "{user_preferences}"
    
    List 3-5 destinations that would be good matches. Return ONLY the destination names as a comma-separated list.
    """
    response = agent.run(prompt)

    destinations = [dest.strip() for dest in response.split(',')]
    logger.info(f"Identified destinations: {destinations}")
    return destinations


def travel_info_searcher(agent, location: str) -> Dict[str, Any]:

    prompt = f"""
    Provide detailed travel information about {location}. Include:
    
    1. Best time to visit
    2. Top 3-5 attractions
    3. Typical accommodation options
    4. Local cuisine highlights
    5. Essential travel tips
    
    Format your response as JSON with these keys: 'best_time', 'attractions', 'accommodation', 'cuisine', 'tips'
    Each value should be a string or list of strings.
    """

    response = agent.run(prompt)

    try:

        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        logger.warning(
            f"Could not parse JSON from response for {location}. Creating structured response.")
        return {
            "best_time": "Information not available",
            "attractions": ["Information not available"],
            "accommodation": ["Information not available"],
            "cuisine": ["Information not available"],
            "tips": ["Information not available"]
        }
    except Exception as e:
        logger.error(f"Error parsing travel info for {location}: {e}")
        return {
            "best_time": "Information not available",
            "attractions": ["Information not available"],
            "accommodation": ["Information not available"],
            "cuisine": ["Information not available"],
            "tips": ["Information not available"]
        }


def travel_plan_generator(agent, user_query: str, destinations: List[str], travel_info: Dict[str, Dict[str, Any]]) -> str:

    prompt = f"""
    Create a detailed travel plan based on:
    
    User Query: {user_query}
    Destinations: {destinations}
    Research Findings: {json.dumps(travel_info)}
    
    Your travel plan should include:
    1. Recommended destinations with rationale
    2. For each destination, provide:
       - Best time to visit
       - Top attractions and activities
       - Accommodation recommendations
       - Local cuisine highlights
       - Travel tips
    
    Format your response as a well-structured travel plan with markdown formatting.
    """

    travel_plan = agent.run(prompt)

    if not travel_plan.strip().startswith("#"):
        travel_plan = "# Custom Travel Plan\n\n" + travel_plan

    return travel_plan


def reflect_on_plan(agent, travel_plan: str, user_query: str) -> Dict[str, Any]:

    prompt = f"""
    Review this travel plan:
    
    {travel_plan}
    
    Based on the user's original query: "{user_query}"
    
    Identify any issues or missing information:
    1. Are all user requirements addressed?
    2. Is any important information missing?
    3. Are there any logical inconsistencies?
    
    Return a JSON with keys: 'issues', 'missing_info', 'improvements'
    Each value should be a list of strings.
    """

    reflection = agent.run(prompt)

    try:

        json_match = re.search(r'```json\n(.*?)\n```', reflection, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        json_match = re.search(r'\{.*\}', reflection, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        logger.warning(
            "Could not parse JSON from reflection. Creating structured response.")
        return {
            "issues": [],
            "missing_info": [],
            "improvements": []
        }
    except Exception as e:
        logger.error(f"Error parsing reflection: {e}")
        return {
            "issues": [],
            "missing_info": [],
            "improvements": []
        }


def improve_travel_plan(agent, travel_plan: str, user_query: str, reflection_data: Dict[str, Any]) -> str:

    if not reflection_data.get('issues') and not reflection_data.get('missing_info'):
        return travel_plan

    prompt = f"""
    Create an improved travel plan that addresses these issues:
    {json.dumps(reflection_data)}
    
    Original query: {user_query}
    
    Original plan:
    {travel_plan}
    
    Your improved travel plan should include all the missing information and fix the identified issues.
    Format your response as a well-structured travel plan with markdown formatting.
    """

    improved_plan = agent.run(prompt)

    if not improved_plan.strip().startswith("#"):
        improved_plan = "# Improved Travel Plan\n\n" + improved_plan

    return improved_plan
