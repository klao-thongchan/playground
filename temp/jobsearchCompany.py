from textwrap import dedent
from crewai import Agent
from langchain_openai import ChatOpenAI

class RecuitmentAgents:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="crewai-llama3-8b"
            base_url="http://localhost:11343/v1"
            api_key="NA"
        )

    def job_hunter_agent(self):
        return Agent(
            role="Job Hunter",
            goal=dedent("""
                Identify relevant job openings across the internet in various domains,
                such as finance, tech, and manufacturing.
            """),
            backstory=dedent("""
                You are an expert at scouring the web for job opportunities. Your competitive drive
                fuels your passion for uncovering every available opening, no matter how obscure
                the source. With your extensive knowledge of online job platforms, databases, and
                networking avenues, you leave no stone unturned in your quest to compile
                comprehensive job listings.
            """),
            tools=[],  
            llm=self.llm,
            verbose=True
        )
    
   def resume_analyst_agent(self):
        return Agent(
            role="Resume Analyst",
            goal=dedent("""
                Efficiently evaluate resumes to identify top candidates for the identified job openings.
            """),
            backstory=dedent("""
                As a seasoned resume analyst, you possess an unparalleled ability to swiftly assess
                candidates' qualifications, experiences, and skills. Your keen eye for detail and
                knack for pattern recognition enable you to breeze through vast volumes of resumes
                with remarkable speed and accuracy. Your expertise lies in meticulously filtering
                the most promising candidates based on predefined criteria, ensuring only the most
                qualified individuals advance to the next stage of the recruitment process.
            """),
            tools=[],  
            llm=self.llm,
            verbose=True
        )

  def company_investigator_agent(self):
        return Agent(
            role="Company Culture Investigator",
            goal=dedent("""
                Uncover insights into organizational culture and values of companies with job openings
                to ensure alignment with candidate expectations.
            """),
            backstory=dedent("""
                As an investigative agent, you possess a keen eye for detail and an insatiable curiosity
                to uncover the inner workings of organizations. Your expertise lies in delving deep into
                company profiles, employee reviews, and industry reports to gain a comprehensive
                understanding of their culture, values, and work environment. Your insights are invaluable
                in ensuring candidates are matched with companies that align with their personal and
                professional aspirations.
            """),
            tools=[],  
            llm=self.llm,
            verbose=True
        )

    def workflow_orchestrator_agent(self):
        return Agent(
            role="Workflow Orchestrator",
            goal=dedent("""
                Coordinate and optimize the recruitment process by synthesizing information
                from all other agents to match candidates with suitable job openings and companies.
            """),
            backstory=dedent("""
                As the strategic mastermind behind our recruitment operations, you possess a unique
                ability to orchestrate workflows and synthesize information from various sources.
                Your role is to seamlessly integrate the efforts of our specialized agents, ensuring
                a cohesive and efficient recruitment process. With your bird's-eye view and analytical
                prowess, you identify optimal candidate-company matches, considering not only qualifications
                but also cultural fit. Your oversight and guidance are instrumental in driving successful
                placements that align with both professional aspirations and organizational values.
            """),
            tools=[],  
            llm=self.llm,
            verbose=True
        )

    def job_search(self, agent):
        return Task(
            description=dedent("""
                Search for job openings in finance, tech, and manufacturing domains across various job websites and platforms.
                Compile a comprehensive list of relevant job opportunities, including job titles, company names, and locations.
                Your output should be a JSON file containing the scraped job opening data, organized by domain.
            """),
            agent=agent,
            expected_output="A JSON file containing job opening data scraped from various job sites, organized by domain.",
            output_file="job_openings.json"
        )

   def resume_analysis(self, agent):
        return Task(
            description=dedent("""
                Analyze the resumes of candidates and filter out the most qualified individuals based on predefined criteria.
                Your analysis should take into account the candidates' qualifications, experiences, and skills in relation to the identified job openings.
                Your output should be a shortlist of top candidates suitable for the job openings.
            """),
            agent=agent,
            expected_output="A shortlist of top candidates suitable for the identified job openings."
        )

    def candidate_outreach(self, agent):
        return Task(
            description=dedent("""
                Craft compelling outreach messages to engage with the shortlisted candidates.
                Your outreach should be personalized, conveying the essence of the job opportunity and the corporate culture in an engaging manner.
                Your output should be the initial contact with potential hires, setting the stage for further recruitment steps.
            """),
            agent=agent,
            expected_output="Initial contact with potential hires, setting the stage for further recruitment steps."
        )

    def company_research(self, agent):
        return Task(
            description=dedent("""
                Investigate the organizational culture and values of companies with job openings.
                Gain a comprehensive understanding of their work environment, employee reviews, and industry reputation.
                Your output should be in-depth company profiles that assist in matching candidates with the right organizational fit.
            """),
            agent=agent,
            expected_output="In-depth company profiles that assist in matching candidates with the right organizational fit."
        )

  def final_matching(self, agent):
        return Task(
            description=dedent("""
                Synthesize the information from the resume analysis and company research tasks.
                Match the shortlisted candidates with suitable job openings and companies based on qualifications and cultural fit.
                Your output should be successful placements that align with both professional aspirations and organizational values.
            """),
            agent=agent,
            expected_output="Successful placement of candidates in roles that align with their professional aspirations and the company's culture."
        )