import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from llm import (
    GroqAgnoAgent,
    SimpleOllamaAgent,
    create_language_model,
    list_models,
    parse_ollama_list,
)


class ParseOllamaListTests(unittest.TestCase):
    def test_object_response_strips_latest(self):
        response = SimpleNamespace(
            models=[SimpleNamespace(model="llama3:latest"), SimpleNamespace(model="mistral")]
        )
        self.assertEqual(parse_ollama_list(response), ["llama3", "mistral"])

    def test_dict_response(self):
        response = {"models": [{"name": "gemma:latest"}]}
        self.assertEqual(parse_ollama_list(response), ["gemma"])


class ListModelsTests(unittest.TestCase):
    def test_hides_groq_without_a_key(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with patch("llm.list_ollama_models", return_value=["llama3"]):
                self.assertEqual(list_models(), ["llama3"])

    @patch("groq.Groq")
    def test_prefixes_groq_chat_models(self, groq_cls):
        groq_cls.return_value.models.list.return_value = SimpleNamespace(
            data=[
                SimpleNamespace(id="llama-3.1-8b-instant"),
                SimpleNamespace(id="whisper-large-v3"),
            ]
        )
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch("llm.list_ollama_models", return_value=["llama3"]):
                self.assertEqual(
                    list_models(),
                    ["llama3", "groq:llama-3.1-8b-instant"],
                )
        self.assertEqual(groq_cls.call_args.kwargs["api_key"], "test-key")


class LanguageModelTests(unittest.TestCase):
    @patch("ollama.generate", return_value={"response": "hello from ollama"})
    @patch("llm.list_ollama_models", return_value=["llama3"])
    def test_ollama_generate(self, _listed, generate):
        agent = create_language_model("llama3")
        self.assertIsInstance(agent, SimpleOllamaAgent)
        self.assertEqual(agent.run("plan a trip"), "hello from ollama")
        generate.assert_called_once_with(model="llama3", prompt="plan a trip")

    def test_groq_without_key_raises(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaises(RuntimeError):
                create_language_model("groq:llama-3.1-8b-instant")

    @patch("agno.agent.Agent")
    @patch("agno.models.groq.Groq")
    def test_groq_runs_through_agno(self, groq_model_cls, agent_cls):
        agent_cls.return_value.run.return_value = SimpleNamespace(
            content="# Lisbon\n\nWalk the river."
        )
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GROQ_BASE_URL": ""}):
            text = GroqAgnoAgent("llama-3.1-8b-instant").run("beaches")
        self.assertIn("Lisbon", text)
        self.assertEqual(groq_model_cls.call_args.kwargs["id"], "llama-3.1-8b-instant")
        self.assertEqual(groq_model_cls.call_args.kwargs["api_key"], "test-key")
        self.assertNotIn("base_url", groq_model_cls.call_args.kwargs)
        self.assertIs(agent_cls.call_args.kwargs["model"], groq_model_cls.return_value)
        self.assertTrue(agent_cls.call_args.kwargs["markdown"])


class TravelPlanContractTests(unittest.TestCase):
    @patch("app.create_language_model")
    def test_simple_plan_is_markdown(self, factory):
        from app import create_travel_plan

        agent = MagicMock()
        agent.run.return_value = "Beach week in Lisbon."
        factory.return_value = agent

        plan = create_travel_plan("beaches in December", "llama3")

        self.assertTrue(plan.lstrip().startswith("#"))
        self.assertIn("Lisbon", plan)
        factory.assert_called_once_with("llama3")

    @patch("app.TravelAgent")
    @patch("app.create_language_model")
    def test_agentic_shape(self, factory, travel_cls):
        from app import create_travel_plan_agentic

        agent = MagicMock()
        agent.model_name = "llama-3.1-8b-instant"
        factory.return_value = agent
        travel_cls.return_value.run_workflow.return_value = {
            "plan": {"destinations": ["Lisbon"], "user_query": "beaches"},
            "research": {"Lisbon": {"best_time": "May"}},
            "initial_plan": "# Draft",
            "reflection": {"issues": [], "missing_info": [], "improvements": []},
            "final_plan": "# Final",
        }

        result = create_travel_plan_agentic("beaches", "groq:llama-3.1-8b-instant")

        self.assertEqual(
            set(result),
            {"plan", "research", "initial_plan", "reflection", "final_plan"},
        )
        travel_cls.assert_called_once_with(agent, model_name="llama-3.1-8b-instant")

    def test_missing_groq_key_returns_fallback(self):
        from app import create_travel_plan

        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            plan = create_travel_plan("beaches", "groq:llama-3.1-8b-instant")
        self.assertIn("Fallback Mode", plan)
        self.assertIn("GROQ_API_KEY", plan)


class ApiContractTests(unittest.TestCase):
    @patch("api.list_models", return_value=["llama3", "groq:llama-3.1-8b-instant"])
    def test_models_route(self, _listed):
        from fastapi.testclient import TestClient
        import api

        response = TestClient(api.app).get("/models")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["models"],
            ["llama3", "groq:llama-3.1-8b-instant"],
        )

    @patch("app.create_travel_plan", return_value="# Plan")
    def test_unified_simple_shape(self, _create):
        from fastapi.testclient import TestClient
        import api

        response = TestClient(api.app).post(
            "/travel-plan-unified",
            json={
                "user_query": "beaches",
                "model_name": "groq:llama-3.1-8b-instant",
                "workflow_type": "Simple",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"travel_plan": "# Plan"})

    @patch(
        "app.create_travel_plan_agentic",
        return_value={
            "plan": {"destinations": ["Lisbon"], "user_query": "beaches"},
            "research": {},
            "initial_plan": "# Draft",
            "reflection": {"issues": [], "missing_info": [], "improvements": []},
            "final_plan": "# Final",
        },
    )
    def test_unified_agentic_shape(self, _create):
        from fastapi.testclient import TestClient
        import api

        response = TestClient(api.app).post(
            "/travel-plan-unified",
            json={
                "user_query": "beaches",
                "model_name": "llama3",
                "workflow_type": "Agentic",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["final_plan"], "# Final")
        self.assertIn("destinations", body["plan"])


if __name__ == "__main__":
    unittest.main()
