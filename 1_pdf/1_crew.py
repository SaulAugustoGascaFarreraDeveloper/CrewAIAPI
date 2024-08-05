from crewai import Agent, Crew, Process, Task
from crewai_tools import PDFSearchTool
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


app = FastAPI()
load_dotenv()


class CrewModel(BaseModel):
    result: str


@app.get("/")
async def root():
    #res = item.result
    # Devolver el resultado almacenado
    if result_from_crew:
        return {"result XD": result_from_crew}
    else:
        return {"message error": "No se ha generado ningún resultado aún."}


@app.post("/api/crew")
async def crew(item: CrewModel):
    # --- Tools ---
    #PDF SOURCE: https://www.gpinspect.com/wp-content/uploads/2021/03/sample-home-report-inspection.pdf
    pdf_search_tool = PDFSearchTool(
        pdf="./example_home_inspection.pdf",
    )

    # --- Agents ---
    research_agent = Agent(
        role="Research Agent",
        goal="Search through the PDF to find relevant answers",
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            The research agent is adept at searching and 
            extracting data from documents, ensuring accurate and prompt responses.
            """
        ),
        tools=[pdf_search_tool],

    )

    professional_writer_agent = Agent(
        role="Professional Writer",
        goal="Write professional emails based on the research agent's findings",
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            The professional writer agent has excellent writing skills and is able to craft 
            clear and concise emails based on the provided information.
            """
        ),
        tools=[],
    )


    # --- Tasks ---
    answer_customer_question_task = Task(
        description=(
            """
            Answer the customer's questions based on the home inspection PDF.
            The research agent will search through the PDF to find the relevant answers.
            Your final answer MUST be clear and accurate, based on the content of the home
            inspection PDF.

            Here is the customer's question:
            {customer_question}
            """
        ),
        expected_output="""
            Provide clear and accurate answers to the customer's questions based on 
            the content of the home inspection PDF.
            """,
        tools=[pdf_search_tool],
        agent=research_agent,
    )

    write_email_task = Task(
        description=(
            """
            - Write a professional email to a contractor based 
                on the research agent's findings.
            - The email should clearly state the issues found in the specified section 
                of the report and request a quote or action plan for fixing these issues.
            - Ensure the email is signed with the following details:
            
                Best regards,

                Brandon Hancock,
                Hancock Realty
            """
        ),
        expected_output="""
            Write a clear and concise email that can be sent to a contractor to address the 
            issues found in the home inspection report.
            """,
        tools=[],
        agent=professional_writer_agent,
    )

    # --- Crew ---
    crew = Crew(
        agents=[research_agent, professional_writer_agent],
        tasks=[answer_customer_question_task, write_email_task],
        process=Process.sequential,
    )

    # customer_question = input(
    #     "Which section of the report would you like to generate a work order for?\n"
    # )
    #res = customer_question
    customer_question = item.result
    global result_from_crew
    result_from_crew = crew.kickoff(inputs={"customer_question": customer_question})
    #result_from_crew = crew.kickoff()
    print(result_from_crew)

    if "but it does not seem to be relevant to the main content of the home inspection report." in result_from_crew.tasks_output[0].raw:
        return "Usa otro termino XD"

    return result_from_crew.tasks_output[0].raw

def main():
    # global result_from_crew
    
    # print(result_from_crew)

     # Aquí puedes continuar con el servidor FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()




