import json
import os
from datetime import datetime
from config import config
from profiles import Profiles
import random 

class MAS:
    def __init__(self, agents, candidate_profiles):
        self.agents = agents
        self.candidates = candidate_profiles
        self.scores = {name: 0 for name in candidate_profiles}
        self.rounds = config["discussion_rounds"]
        self.target_profile = Profiles.Target_Profile
        
        self.prior_reflections = {}
        self.prior_debates = {}
        self.session_logs = []

    def conduct_round(self, round_number):
        print(f"\n🔄 Conducting Round {round_number}")

        context = f"Round {round_number} with previous reflections: {json.dumps(self.prior_reflections)} and debates: {json.dumps(self.prior_debates)}"

        # Initialization of log entry
        log_entry = {
            "round": round_number,
            "evaluations": {},
            "reflections": {},
            "debates": {}
        }

        # First evaluations per agent
        for agent in self.agents:
            log_entry["evaluations"][agent.name] = {}

        # Evaluations
        for agent in self.agents:
            prior_reflection = self.prior_reflections.get(agent.name, {})
            prior_debate = self.prior_debates.get(agent.name, {})

            for candidate, profile in self.candidates.items():
                evaluation = agent.evaluate_candidate(
                    candidate_name=candidate,
                    candidate_profile=profile,
                    target_profile=self.target_profile,
                    context=context,
                    prior_reflection=prior_reflection if round_number > 1 else None,
                    prior_debate=prior_debate if round_number > 1 else None
                )

                total = sum([
                    evaluation.get("integrity_score", 0),
                    evaluation.get("capability_score", 0),
                    evaluation.get("fit_score", 0)
                ])
                self.scores[candidate] = total

                log_entry["evaluations"][agent.name][candidate] = evaluation
                print(f"📝 {agent.name} evaluated {candidate}: Total Score = {total}")

        # Reflections
        current_reflections = {}
        for agent in self.agents:
            reflection = agent.reflect(log_entry["evaluations"][agent.name], context)
            current_reflections[agent.name] = reflection
            log_entry["reflections"][agent.name] = reflection
            print(f"\n🔍 Reflection from {agent.name}: {json.dumps(reflection, indent=2)}")

        # Debates
        current_debates = {}
        for agent in self.agents:
            debate = agent.debate(log_entry["evaluations"], context)
            current_debates[agent.name] = debate
            log_entry["debates"][agent.name] = debate
            print(f"\n💬 Debate inputs from {agent.name}: {json.dumps(debate, indent=2)}")

        # Update prior reflections and debates for next round
        self.prior_reflections, self.prior_debates = current_reflections, current_debates

        # Add to session logs (but don't save each round)
        self.session_logs.append(log_entry)

    def finalize_shortlist(self):
        # Rank by scores
        ranked = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        shortlist = []

        # Handle ties clearly
        top_k = config["shortlist_top_k"]
        if len(ranked) <= top_k:
            shortlist = [candidate for candidate, _ in ranked]
        else:
            cutoff_score = ranked[top_k - 1][1]
            shortlist = [candidate for candidate, score in ranked if score >= cutoff_score]

            # If tie occurs (shortlist bigger than top_k)
            if len(shortlist) > top_k:
                print("\n⚠️ Multiple Ties Detected in Final Round!")
                
                # Apply tie-breaking clearly based on capability, integrity, fit
                tie_candidates = {c: self.scores[c] for c in shortlist}
                tie_break_scores = {c: {"capability": 0, "integrity": 0, "fit": 0} for c in shortlist}

                # Extract latest evaluations to break tie
                for entry in reversed(self.session_logs):
                    if 'evaluations' in entry:
                        for agent_evals in entry['evaluations'].values():
                            for candidate, eval_scores in agent_evals.items():
                                if candidate in shortlist:
                                    tie_break_scores[candidate]["capability"] += eval_scores["capability_score"]
                                    tie_break_scores[candidate]["integrity"] += eval_scores["integrity_score"]
                                    tie_break_scores[candidate]["fit"] += eval_scores["fit_score"]
                        break  # only the latest round of evaluation

                # Sort tie candidates by capability, then integrity, then fit
                tie_sorted = sorted(
                    shortlist,
                    key=lambda c: (
                        tie_break_scores[c]["capability"], 
                        tie_break_scores[c]["integrity"], 
                        tie_break_scores[c]["fit"]
                    ),
                    reverse=True
                )
                
                shortlist = tie_sorted[:top_k]

                # If still completely tied, random choice clearly
                if len(set(self.scores[c] for c in shortlist)) == 1:
                    print("\n⚠️ Final tie still remains after detailed tie-breakers! Using random selection.")
                    shortlist = random.sample(shortlist, top_k)

        # Save final selection and print clearly
        self.session_logs.append({"final_scores": self.scores, "shortlist": shortlist})
        self.save_log()

        print("\n🎯 [Final Shortlisted Candidates (with ties handled)]:")
        for candidate in shortlist:
            print(f"- {candidate}")

        return shortlist


    def save_log(self):
        logs_folder = "logs"
        os.makedirs(logs_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"MAS_Log_Final_{timestamp}.json"
        filepath = os.path.join(logs_folder, filename)

        with open(filepath, 'w') as log_file:
            json.dump(self.session_logs, log_file, indent=2)

        print(f"\n📌 Final log saved at: {filepath}")