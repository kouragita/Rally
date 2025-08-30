import requests
import json
import time
import os
import sys
from fpdf import FPDF

BASE_URL = "http://127.0.0.1:8000/api/v1"
REPORTS_DIR = "reports"

# Ensure the reports directory exists
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AI Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def open_pdf(filepath):
    """
    Opens the generated PDF file using the default system viewer.
    """
    if sys.platform == "win32":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        os.system(f"open {filepath}")
    else: # linux
        os.system(f"xdg-open {filepath}")

def test_ecosystem_analysis():
    """
    Tests the AI-powered analysis for an aquatic ecosystem,
    aligning with the user's prompt about classifying data and querying changes.
    """
    print("\n--- Testing Ecosystem Analysis (Aquatic) ---")
    endpoint = f"{BASE_URL}/analysis/"
    payload = {
        "query": "What are the main climate change impacts on pelagic marine systems, and how do these changes affect aquatic species? Provide current percentages of impact and suggest predictive analyses for mitigation.",
        "target_type": "ecosystem",
        "target_name": "Pelagic Marine Systems"
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        print("Ecosystem Analysis Request Successful:")
        print(json.dumps(result, indent=2))
        return result.get("report_id")
    except requests.exceptions.RequestException as e:
        print(f"Error during ecosystem analysis: {e}")
        return None

def test_species_analysis():
    """
    Tests the AI-powered analysis for a specific species,
    aligning with the user's prompt about species endangerment, causes, and climate changes.
    """
    print("\n--- Testing Species Analysis (Polar Bear) ---")
    endpoint = f"{BASE_URL}/analysis/"
    payload = {
        "query": "Assess the current endangerment level of the Polar Bear. What are the primary causes of its population decline, including climate-related disruptions? Provide current percentages of decline and a predictive analysis for its future.",
        "target_type": "species",
        "target_name": "Ursus maritimus"
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        result = response.json()
        print("Species Analysis Request Successful:")
        print(json.dumps(result, indent=2))
        return result.get("report_id")
    except requests.exceptions.RequestException as e:
        print(f"Error during species analysis: {e}")
        return None

def generate_report_pdf(report_data: dict, filename: str):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Calculate available width for multi_cell
    available_width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Report ID: {report_data.get('id', 'N/A')}", 0, 1)
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Query Parameters:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(available_width, 8, f"Query: {report_data.get('query', 'N/A')}")
    pdf.multi_cell(available_width, 8, f"Ecosystem: {report_data.get('ecosystem', 'N/A')}")
    pdf.multi_cell(available_width, 8, f"Species: {report_data.get('species', 'N/A')}")
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Metrics:', 0, 1)
    pdf.set_font('Arial', '', 12)
    metrics = report_data.get('metrics', {})
    pdf.multi_cell(available_width, 8, f"Temperature Change: {metrics.get('temperatureChange', 'N/A')}°C")
    pdf.multi_cell(available_width, 8, f"Precipitation Change: {metrics.get('precipitationChange', 'N/A')}%")
    pdf.multi_cell(available_width, 8, f"Species at Risk: {metrics.get('speciesAtRisk', 'N/A')}")
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Key Insights:', 0, 1)
    pdf.set_font('Arial', '', 12)
    insights = report_data.get('insights', [])
    if insights:
        for i, insight in enumerate(insights):
            pdf.multi_cell(available_width, 8, f"- {insight}")
    else:
        pdf.multi_cell(available_width, 8, "No insights available.")
    pdf.ln(5)

    # Charts Data (represented as text/tables)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Charts Data:', 0, 1)
    pdf.set_font('Arial', '', 12)
    charts = report_data.get('charts', {})

    if charts.get('temperature'):
        pdf.multi_cell(available_width, 8, "Temperature Data:")
        for item in charts['temperature']:
            pdf.multi_cell(available_width, 8, f"  - {item.get('name')}: {item.get('value')}")
        pdf.ln(2)

    if charts.get('population'):
        pdf.multi_cell(available_width, 8, "Population Data:")
        for item in charts['population']:
            pdf.multi_cell(available_width, 8, f"  - {item.get('name')}: {item.get('value')}")
        pdf.ln(2)

    # Raw AI Text (if available in analysis_results)
    if 'analysis_results' in report_data and 'raw_text' in report_data['analysis_results']:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Raw AI Analysis Text:', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(available_width, 8, report_data['analysis_results']['raw_text'])
        pdf.ln(5)

    pdf_path = os.path.join(REPORTS_DIR, filename)
    pdf.output(pdf_path)
    print(f"Report saved to {pdf_path}")
    open_pdf(pdf_path) # Open the PDF after saving

def get_report(report_id: int, report_type: str):
    """
    Retrieves a previously generated AI analysis report and generates a PDF.
    """
    print(f"\n--- Fetching Report ID: {report_id} ---")
    endpoint = f"{BASE_URL}/reports/{report_id}"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        report = response.json()
        print("Report Retrieved Successfully:")
        print(json.dumps(report, indent=2))

        # Generate PDF
        pdf_filename = f"analysis_report_{report_type}_{report_id}.pdf"
        generate_report_pdf(report, pdf_filename)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching report {report_id}: {e}")

def main():
    print("Starting AI Analysis Test Script...")
    print("Ensure your backend server is running at http://127.0.0.1:8000")
    print("You can also check the API documentation at http://127.0.0.1:8000/docs")

    # Test Ecosystem Analysis
    ecosystem_report_id = test_ecosystem_analysis()
    if ecosystem_report_id:
        print("\nWaiting for 5 seconds for report generation...")
        time.sleep(5)
        get_report(ecosystem_report_id, "ecosystem")

    print("\n" + "="*50 + "\n")

    # Test Species Analysis
    species_report_id = test_species_analysis()
    if species_report_id:
        print("\nWaiting for 5 seconds for report generation...")
        time.sleep(5)
        get_report(species_report_id, "species")

    print("\nAI Analysis Test Script Finished.")

if __name__ == "__main__":
    main()
