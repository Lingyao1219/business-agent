from agent import Agent
from mas import MAS
from profiles import Profiles
from config import config

def main():
    agents = []

    for agent_conf in config["agents"]:
        agent = Agent(
            name=agent_conf["name"],
            role=agent_conf["role"],
            ability=agent_conf["ability"],
            profile=agent_conf["profile"]
        )
        agents.append(agent)

    candidates = Profiles.Candidate_Profiles
    mas_system = MAS(agents, candidates)

    for round_num in range(1, mas_system.rounds + 1):
        mas_system.conduct_round(round_num)

    mas_system.finalize_shortlist()

if __name__ == "__main__":
    main()