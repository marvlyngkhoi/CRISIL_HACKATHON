import gradio as gr
from finance_report import generate_report
from forcaster import gradio_interface

# Gradio App
def main():
    with gr.Blocks() as app:
        gr.Markdown("## Financial Toolkit")
        with gr.Tabs():
            with gr.Tab("Generate Report"):
                company = gr.Textbox(label="Company Name", placeholder="NextEra")
                competitors = gr.Textbox(label="Competitors (comma-separated)",placeholder="""["DUK","CEG","AEP"]""")
                fyear = gr.Textbox(label="Fiscal Year",placeholder="2024")
                report_output_image = gr.Image(label="Generated Report Page 1")
                report_output_file = gr.File(label="Download PDF")
                report_button = gr.Button("Generate Report")
                report_button.click(
                    generate_report,
                    inputs=[company, competitors, fyear],
                    outputs=[report_output_image, report_output_file],
                )

            with gr.Tab("Market Analysis"):
                company_input = gr.Textbox(label="Enter Company Name", placeholder="e.g., Tesla")
                analysis_output = gr.Textbox(label="Market Analysis Output", lines=10)
                analysis_button = gr.Button("Analyze Market")
                analysis_button.click(
                    gradio_interface,
                    inputs=[company_input],
                    outputs=[analysis_output],
                )

    app.launch(share=True)


if __name__ == "__main__":
    main()
