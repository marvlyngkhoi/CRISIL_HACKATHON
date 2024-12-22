import gradio as gr
import autogen
from autogen.cache import Cache
from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.data_source import FinnHubUtils, YFinanceUtils
from finrobot.toolkits import register_toolkits

# Read OpenAI API keys from a JSON file
config_list = autogen.config_list_from_json(
    "./OAI_CONFIG_LIST",
    filter_dict={"model": ["gpt-4-0125-preview"]},
)
llm_config = {"config_list": config_list, "timeout": 120, "temperature": 0}

# Register FINNHUB API keys
register_keys_from_json("./config_api_keys")

analyst = autogen.AssistantAgent(
    name="Market_Analyst",
    system_message=(
        "As a Market Analyst, one must possess strong analytical and problem-solving abilities, "
        "collect necessary financial information and aggregate them based on client's requirement. "
        "For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done."
    ),
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
)

# Define tools
tools = [
    {
        "function": FinnHubUtils.get_company_profile,
        "name": "get_company_profile",
        "description": "get a company's profile information",
    },
    {
        "function": FinnHubUtils.get_company_news,
        "name": "get_company_news",
        "description": "retrieve market news related to designated company",
    },
    {
        "function": FinnHubUtils.get_basic_financials,
        "name": "get_financial_basics",
        "description": "get latest financial basics for a designated company",
    },
    {
        "function": YFinanceUtils.get_stock_data,
        "name": "get_stock_data",
        "description": "retrieve stock price data for designated ticker symbol",
    },
]
register_toolkits(tools, analyst, user_proxy)

# def analyze_market(company):
#     with Cache.disk() as cache:
#         response = user_proxy.initiate_chat(
#             analyst,
#             message=(
#                 f"Use all the tools provided to retrieve information available for {company} upon {get_current_date()}. "
#                 "Analyze the positive developments and potential concerns of {company} with 2-4 most important factors respectively and keep them concise. "
#                 "Most factors should be inferred from company-related news. Then make a rough prediction (e.g., up/down by 2-3%) of the {company} stock price movement for next week. "
#                 "Provide a summary analysis to support your prediction."
#             ),
#             cache=cache,
#         )
       
#         return response
def analyze_market(company):
    with Cache.disk() as cache:
        response = user_proxy.initiate_chat(
            analyst,
            message=(
                f"Use all the tools provided to retrieve information available for {company} upon {get_current_date()}. "
                "Analyze the positive developments and potential concerns of {company} with 2-4 most important factors respectively and keep them concise. "
                "Most factors should be inferred from company-related news. Then make a rough prediction (e.g., up/down by 2-3%) of the {company} stock price movement for next week. "
                "Provide a summary analysis to support your prediction."
            ),
            cache=cache,
        )
        # for msg in response.chat_history:
        #     if msg and isinstance(msg, dict) and "content" in msg and msg["content"]:
        #         if "Based on the information retrieved:" in msg["content"]:
        #             return msg["content"]
        # return "No relevant analysis found or an error occurred during the analysis process."
        return response



    
def gradio_interface(company):
    response = analyze_market(company)
    #print(response.chat_history[-3])
    return response.chat_history[-3]['content']

# # Gradio app
# def main():
#     with gr.Blocks() as demo:
#         gr.Markdown("## Market Analysis App")
#         company_input = gr.Textbox(label="Enter the company name", placeholder="e.g., Tesla, Apple")
#         output = gr.Textbox(label="Market Analysis Output", lines=10)
#         submit_button = gr.Button("Analyze")

#         submit_button.click(gradio_interface, inputs=[company_input], outputs=[output])

#     demo.launch()

# if __name__ == "__main__":
#     main()
