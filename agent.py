from utils import call_model, parse_llm_response
import json

class Agent:
    def __init__(self, name, role, ability, profile):
        self.name = name
        self.role = role
        self.ability = ability
        self.profile = profile 

    def evaluate_candidate(self, candidate_name, candidate_profile, target_profile, context, prior_reflection=None, prior_debate=None):
        reflection_debate_context = ""
        
        # Include prior reflection and debate context if available
        if prior_reflection or prior_debate:
            reflection_debate_context = f"""
Prior Reflection from you: 
{json.dumps(prior_reflection, indent=2)}

Prior Debate inputs from peers:
{json.dumps(prior_debate, indent=2)}

Given the new information, explicitly state whether you adjust any score compared to last round or maintain the scores. Provide clear rationale for your decision.
            """

        prompt = f"""
You are '{self.name}', {self.role}, possessing {self.ability}. Evaluate candidate '{candidate_name}' for potential investment as follows:

# Scoring Guidance (1-5 scale)
- 1: Poor match, significant concerns, not recommended at all.
- 2: Below average, considerable issues, generally not favorable.
- 3: Average neutrality, acceptable but with clear reservations.
- 4: Good candidate, strong fit with minimal concerns.
- 5: Excellent candidate, ideal investment partner and highly recommended.

# Investment Target:
{target_profile}

# Your Company Profile:
{self.profile}

# Candidate Company Profile:
{candidate_profile}

# Additional Context:
{context}

{reflection_debate_context}

# Evaluation to be strictly JSON formatted:
{{
  "integrity_score": int (1-5),
  "integrity_rationale": "... clear rationale why this score was given ...",
  
  "capability_score": int (1-5),
  "capability_rationale": "... clear rationale why this score was given ...",
  
  "fit_score": int (1-5),
  "fit_rationale": "... clear rationale why this score was given ...",
  
  "score_adjustment": "... if applicable, clearly state whether you changed or maintained scores from prior round, and rationale ..."
}}
        """

        response = call_model(prompt)
        return parse_llm_response(response)

    def reflect(self, evaluations, context):
        prompt = f"""
You are '{self.name}', ({self.role}). After reviewing your evaluations:

Evaluations:
{json.dumps(evaluations, indent=2)}

Context:
{context}

Reflect critically on the evaluations. Provide clear thoughts in strictly JSON:
{{
"reflection_summary": "... comprehensive reflection on possible biases, assumptions, or key insights ...",
"improvement_suggestions": ["clear suggestions on improvement", "... more thoughtful suggestion"]
}}
        """

        return parse_llm_response(call_model(prompt))

    def debate(self, all_agents_evaluations, context):
        prompt = f"""
You '{self.name}' ({self.role}) review evaluations by peers:

All Agents' Evaluations:
{json.dumps(all_agents_evaluations, indent=2)}

Context:
{context}

Critically analyze your peers' evaluations, clearly state points you agree or disagree with, and ask relevant questions to clarify their points. Output as strictly formatted JSON:
{{
  "agree": ["agent_name: reason why you agree clearly stated"],
  "disagree": ["agent_name: clearly stated disagreement and rationale"],
  "questions": ["concise question directed clearly to agent_name about unclear or interesting viewpoint"]
}}
        """

        return parse_llm_response(call_model(prompt))