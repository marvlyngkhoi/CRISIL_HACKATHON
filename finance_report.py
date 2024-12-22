import gradio as gr
import os
import autogen
from finrobot.utils import register_keys_from_json
from finrobot.toolkits import register_toolkits
from finrobot.functional import (
    ReportChartUtils,
    ReportAnalysisUtils,
    IPythonUtils,
    ReportLabUtils,
    TextUtils,
)
from finrobot.data_source import FMPUtils
from textwrap import dedent
import fitz
from PIL import Image
import io

def generate_report(company, competitors, fyear):
    work_dir = "./report"
    os.makedirs(work_dir, exist_ok=True)

    system_message = dedent(f"""
        You are a trading strategist known for your expertise in developing sophisticated trading algorithms. 
        Your task is to leverage your coding skills to create a customized trading strategy using the BackTrader Python library, and save it as a Python module. 
        Remember to log necessary information in the strategy so that further analysis could be done.
        You can also write custom sizer / indicator and save them as modules, which would allow you to generate more sophisticated strategies.
        After creating the strategy, you may backtest it with the tool you're provided to evaluate its performance and make any necessary adjustments.
        All files you created during coding will automatically be in `{work_dir}`, no need to specify the prefix. 
        But when calling the backtest function, module path should be like `{work_dir.strip('/')}.<module_path>` and savefig path should consider `{work_dir}` as well.
        Reply TERMINATE to executer when the strategy is ready to be tested.
        """)

    config_list = autogen.config_list_from_json(
        "./OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4-0125-preview"],
        },
    )
    llm_config = {
        "config_list": config_list,
        "timeout": 120,
        "temperature": 0.5,
    }
    register_keys_from_json("./config_api_keys")

    expert = autogen.AssistantAgent(
        name="Expert_Investor",
        system_message=system_message,
        llm_config=llm_config,
        is_termination_msg=lambda x: x.get("content", "")
        and x.get("content", "").endswith("TERMINATE"),
    )
    expert_shadow = autogen.AssistantAgent(
        name="Expert_Investor_Shadow",
        system_message=system_message,
        llm_config=llm_config,
    )
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        code_execution_config={
            "last_n_messages": 1,
            "work_dir": work_dir,
            "use_docker": False,
        },
    )

    register_toolkits(
        [
            FMPUtils.get_sec_report,
            IPythonUtils.display_image,
            TextUtils.check_text_length,
            ReportLabUtils.build_annual_report,
            ReportAnalysisUtils,
            ReportChartUtils,
        ],
        expert,
        user_proxy,
    )

    # Define the trigger and message functions for nested chat
    def order_trigger(sender):
        # Check if the last message contains the path to the instruction text file
        return "instruction & resources saved to" in sender.last_message()["content"]

    def order_message(recipient, messages, sender, config):
        # Extract the path to the instruction text file from the last message
        full_order = recipient.chat_messages_for_summary(sender)[-1]["content"]
        txt_path = full_order.replace("instruction & resources saved to ", "").strip()
        with open(txt_path, "r") as f:
            instruction = f.read() + "\n\nReply TERMINATE at the end of your response."
        return instruction

    # Register nested chats for detailed analysis
    expert.register_nested_chats(
        [
            {
                "sender": expert,
                "recipient": expert_shadow,
                "message": order_message,
                "summary_method": "last_msg",
                "max_turns": 2,
                "silent": True,  # mute the chat summary
            }
        ],
        trigger=order_trigger,
    )

    task = dedent(
        f"""
        With the tools you've been provided, write an annual report based on {company}'s and {competitors}  {fyear} 10-k report, format it into a pdf.
        Pay attention to the followings:
        - Explicitly explain your working plan before you kick off.
        - Use tools one by one for clarity, especially when asking for instructions.
        - All your file operations should be done in "{work_dir}".
        - Display any image in the chat once generated.
        - For competitors analysis, strictly follow my prompt and use data only from the financial metrics table, do not use similar sentences in other sections.
        - Each paragraph in the first page should be between 150 and 160 words, and in the second page between 500 and 600 words.
        """
    )

    with autogen.Cache.disk() as cache:
        user_proxy.initiate_chat(
            recipient=expert, message=task, max_turns=50, summary_method="last_msg"
        )

    pdf_path = f"{work_dir}/{company}_Annual_Report_{fyear}.pdf"

    # Extract the first page as an image to display
    with fitz.open(pdf_path) as pdf:
        page = pdf[0]
        pix = page.get_pixmap()
        image = Image.open(io.BytesIO(pix.tobytes("png")))

    return image, pdf_path


# def main():
#     interface = gr.Interface(
#         fn=generate_report,
#         inputs=[
#             gr.Textbox(label="Company Name"),
#             gr.Textbox(label="Competitors (comma-separated)"),
#             gr.Textbox(label="Fiscal Year"),
#         ],
#         outputs=[
#             gr.Image(label="Generated Report Page 1"),
#             gr.File(label="Download PDF"),
#         ],
#         title="Financial Report Generator",
#         description="Generate a financial report PDF and visualize its first page. Download the full report as a PDF file.",
#     )
#     interface.launch(share=True)

# if __name__ == "__main__":
#     main()
