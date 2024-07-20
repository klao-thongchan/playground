


class RecruitmentAgents:
    """
    Class to create agents involved in the recruitment process.

    Attributes:
        - use_groq (bool): Flag indicating whether to use the GROQ model for language processing.
    """

    def __init__(self, use_groq=False):
        """
        Initialize RecruitmentAgents.

        Args:
            use_groq (bool): Flag indicating whether to use the GROQ model for language processing.
        """
        load_dotenv()

        # Initialize llm based on the flag
        if use_groq:
            self.llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model="llama3-70b-8192"
            )
        else:
            self.llm = ChatOpenAI(
                model="crewai-llama3-8b",
                base_url="http://localhost:11434/v1",
                api_key="NA"
            )

    def job_hunter_agent(self):
        """
        Create an agent responsible for identifying relevant job openings across the internet.

        Returns:
            Agent: An Agent object representing the job hunter agent.
        """
        api_key = os.getenv("SERPAPI_API_KEY")
        google_jobs_tool = JobScrapeQueryRun(api_key)
        wrapped_tool = Tool(
            name="Google Jobs Search",
            func=google_jobs_tool.extract_multiple_jobs,
            description="Search for job openings on Google Jobs. Input should be a dictionary with keys 'query' and 'location'."
        )

        return Agent(
            role="Job Hunter",
            goal=dedent("""
                Identify relevant job openings across the internet in various domains,
                such as finance, tech, and cyber security. Gather detailed information about
                each job opening, including required skills, qualifications, and salary range
                (if available).
            """),
            backstory=dedent("""
                You are an expert at scouring the web for job opportunities. Your competitive drive
                fuels your passion for uncovering every available opening, no matter how obscure
                the source. With your extensive knowledge of online job platforms, databases, and
                networking avenues, you leave no stone unturned in your quest to compile
                comprehensive job listings with detailed information about each role.
            """),
            tools=[wrapped_tool],
            llm=self.llm,
            verbose=True,
            max_iterations=25,
            early_stopping_method="force"
        )

    def resume_analyst_agent(self):
        """
        Create an agent responsible for efficiently evaluating resumes to identify top candidates.

        Returns:
            Agent: An Agent object representing the resume analyst agent.
        """
        resume_file_read_tool = FileReadTool(file_path="database/company_resume_store.json")
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
            tools=[resume_file_read_tool],
            llm=self.llm,
            verbose=True,
            max_iterations=25
        )

    def candidate_engagement_agent(self):
        """
        Create an agent responsible for crafting compelling outreach messages to engage potential candidates.

        Returns:
            Agent: An Agent object representing the candidate engagement specialist agent.
        """
        return Agent(
            role="Candidate Engagement Specialist",
            goal=dedent("""
                Craft compelling outreach messages to engage potential candidates identified
                by the Resume Analyst.
            """),
            backstory=dedent("""
                With your exceptional communication skills and flair for writing, you excel at
                crafting irresistible outreach messages that capture the attention of top talent.
                Your deep understanding of human psychology allows you to tailor your correspondence,
                striking the perfect balance between professionalism and charisma. Your ability to
                convey the essence of a job opportunity and the corporate culture in a compelling
                manner sets the stage for successful candidate engagement.
            """),
            tools=[],
            llm=self.llm,
            verbose=True,
            max_iterations=25
        )
    
    def company_investigator_agent(self):
        """
        Create an agent responsible for uncovering insights into the organizational culture and values of companies.

        Returns:
            Agent: An Agent object representing the company culture investigator agent.
        """
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
            verbose=True,
            max_iterations=25
        )
    
    def workflow_orchestrator_agent(self):
        """
        Create an agent responsible for coordinating and optimizing the recruitment process.

        Returns:
            Agent: An Agent object representing the workflow orchestrator agent.
        """
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
            verbose=True,
            max_iterations=25
        )