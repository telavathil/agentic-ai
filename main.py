"""Main module for the agent."""

import asyncio
import logging
import sys
from agent.core.agent import Agent

def setup_logging(debug: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('agent.log', mode='a')  # Add file logging
        ]
    )

    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

async def main():
    """Main function for the agent."""
    # Set up logging with debug mode
    setup_logging(debug=True)
    logger = logging.getLogger(__name__)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info("Initializing agent...")
            agent = Agent()

            # Test with a simple task
            task = """
            Calculate the compound interest on $1000 with 5% annual interest rate for 3 years
            """
            logger.info("Processing task: %s", task)
            result = await agent.process_task(task)

            logger.info("Task completed successfully")
            print("\n=== Final Response ===")
            print(result["final_response"])

            print("\n=== Detailed Results ===")
            for step_result in result["results"]:
                step = step_result["step"]
                result = step_result["result"]
                print(f"\nStep {step['step_id']}: {step['description']}")
                print(f"Status: {result['status']}")
                print(f"Output: {result['output']}")

            return  # Success, exit the retry loop

        except (ValueError, SyntaxError, TypeError) as e:
            logger.error("Attempt %d/%d failed: %s", attempt + 1, max_retries, e, exc_info=True)

            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                logger.info("Waiting %d seconds before retrying...", wait_time)
                await asyncio.sleep(wait_time)
            else:
                logger.error("Max retries reached. Task failed.")
                raise

if __name__ == "__main__":
    asyncio.run(main())
