def create_dummy_resumes(num_resumes):
    """
    Generate dummy resumes.

    Args:
        num_resumes (int): Number of resumes to generate.

    Returns:
        list: List of dummy resumes, each containing name, qualifications, experiences, and skills.
    """
    resumes = []
    for i in range(num_resumes):
        resume = {
            "name": f"Candidate {i+1}",
            "qualifications": ["Qualification 1", "Qualification 2"],
            "experience": ["Experience 1", "Experience 2"],
            "skills": ["Skill 1", "Skill 2"]
        }
        resumes.append(resume)
    return resumes


def save_data(resumes, job_openings):
    """
    Save resume and job opening data to JSON files.

    Args:
        resumes (list): List of resumes to be saved.
        job_openings (dict): Dictionary containing job openings to be saved.
    """
    with open("resumes.json", "w") as f:
        json.dump(resumes, f, indent=2)
    with open("job_openings.json", "w") as f:
        json.dump(job_openings, f, indent=2)


def load_data():
    """
    Load resume and job opening data from JSON files.

    Returns:
        tuple: A tuple containing two elements: resumes (list) and job_openings (dict).
    """
    with open("resumes.json", "r") as f:
        resumes = json.load(f)
    with open("job_openings.json", "r") as f:
        job_openings = json.load(f)
    return resumes, job_openings

# Create dummy data
num_resumes = 10
num_jobs    = 15
resumes         = create_dummy_resumes(num_resumes)
job_openings    = create_dummy_job_openings(num_jobs)
save_data(resumes, job_openings)

# Load data from files
resumes, job_openings = load_data()

# Create agents
recruitment_agents      = RecruitmentAgents(use_groq=False)
job_hunter              = recruitment_agents.job_hunter_agent()
resume_analyst          = recruitment_agents.resume_analyst_agent()
candidate_engagement    = recruitment_agents.candidate_engagement_agent()
company_investigator    = recruitment_agents.company_investigator_agent()
workflow_orchestrator   = recruitment_agents.workflow_orchestrator_agent()

# Create tasks
recruitment_tasks       = RecruitmentTasks()
job_search_task         = recruitment_tasks.job_search(job_hunter)
resume_analysis_task    = recruitment_tasks.resume_analysis(resume_analyst)
candidate_outreach_task = recruitment_tasks.candidate_outreach(candidate_engagement)
company_research_task   = recruitment_tasks.company_research(company_investigator)
final_matching_task     = recruitment_tasks.final_matching(workflow_orchestrator)

# Create crew
recruitment_crew = Crew(
    agents=[job_hunter, resume_analyst, candidate_engagement, company_investigator, workflow_orchestrator],
    tasks=[job_search_task, job_search_task, resume_analysis_task, candidate_outreach_task, company_research_task, final_matching_task],
    verbose=True
)

# Run the recruitment process
result = recruitment_crew.kickoff()

# Print the results
print("\n\n-------------------------------------")
print("## Final Results")
print("\n\n-------------------------------------")
print(result)
print("\n\n-------------------------------------")