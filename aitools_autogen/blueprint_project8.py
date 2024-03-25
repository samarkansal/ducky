from typing import Optional
import asyncio
import autogen
from autogen import ConversableAgent
from aitools_autogen.blueprint import Blueuprint
from aitools_autogen.config import llm_config, config_list, WORKING_DIR
from aitools_autogen.utils import save_code_files, summarize_files, clear_working_dir


class LeetCodeBlueprint(Blueprint):

    def __init__(self, work_dir: Optional[str] = WORKING_DIR):
        super().__init__([], config_list=config_list, llm_config=llm_config)
        self._work_dir = work_dir or WORKING_DIR
        self._summary_result: Optional[str] = None

    @property
    def summary_result(self) -> str | None:
        return self._summary_result

    @property
    def work_dir(self) -> str:
        return self._work_dir

    async def initiate_work(self, message: str):
        clear_working_dir(self._work_dir)

        # Agents
        scraper = autogen.AssistantAgent("scraper", max_consecutive_auto_reply=50,
                                         llm_config=llm_config,
                                         system_message="""
            You are a web scraping expert tasked with extracting detailed information from a given LeetCode problem URL. 
            Your job is to retrieve the complete problem statement, including the description, input/output formats, constraints, and any provided example cases. 
            Pay attention to details like edge cases mentioned in the problem, specific formatting requirements, and any hints or notes included in the problem description. 
            Your output should be a comprehensive summary of the problem, formatted clearly and concisely for the next agent to generate test cases.
        """)

        test_case_generator = autogen.AssistantAgent("test_case_generator", max_consecutive_auto_reply=50,
                                                     llm_config=llm_config,
                                                     system_message="""
            You specialize in creating comprehensive test cases for programming problems. 
            Based on the detailed problem description provided by the scraper agent, your task is to generate a set of 20-30 test cases that cover all aspects of the problem. 
            These should include typical cases, edge cases, boundary conditions, and any special scenarios mentioned in the problem description. 
            Your test cases should be diverse and challenging enough to thoroughly evaluate the robustness of any proposed solution. Output these test cases in a structured format (e.g., JSON, CSV, or plain text) suitable for automated processing by the problem solver agent.
            """)

        problem_solver = autogen.AssistantAgent("problem_solver", max_consecutive_auto_reply=50,
                                                llm_config=llm_config,
                                                system_message="""You are an expert Python programmer with a task to 
                                                develop a solution for the LeetCode problem described by the scraper 
                                                agent. Your input is the file of test cases generated by the test 
                                                case generator. Write a Python script that reads these test cases and 
                                                implements an efficient solution to the problem. Your code should be 
                                                clean, well-commented, and follow best programming practices. It 
                                                should handle all test cases correctly, demonstrating the solution's 
                                                correctness and efficiency. Once you have a solution, test it against 
                                                the provided test cases, ensuring that it passes all of them. Output 
                                                your final solution script, including any necessary comments or 
                                                explanations. Only output the final script that passes all test cases.""" )

        # Group chat setup
        groupchat = autogen.GroupChat(agents=[scraper, test_case_generator, problem_solver], messages=[], max_round=15)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        manager.initiate_chat(scraper, True, False, message=message)

        # Process messages and save the code files
        for msg in scraper.chat_messages[manager]:
            save_code_files(msg['content'], self._work_dir)
        # Additional loop for test_case_generator and problem_solver
        for msg in test_case_generator.chat_messages[manager]:
            save_code_files(msg['content'], self._work_dir)
        for msg in problem_solver.chat_messages[manager]:
            save_code_files(msg['content'], self._work_dir)

        # Summarize the results
        self._summary_result = summarize_files(self._work_dir)


if __name__ == "__main__":
    blueprint = LeetCodeBlueprint()
    # Prompt user for a LeetCode URL or use the default
    leetcode_url = input("Enter a LeetCode problem URL (or press Enter to use the default): ")
    if not leetcode_url.strip():
        leetcode_url = "https://leetcode.com/problems/longest-substring-without-repeating-characters/"

    asyncio.run(blueprint.initiate_work(message=f"""
            Scrape the problem details from the following LeetCode URL: {leetcode_url}.
            Generate test cases and solve the problem in Python, ensuring all test cases pass.
        """))
    print(blueprint.summary_result)