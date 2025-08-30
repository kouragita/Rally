import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

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

def get_report(report_id: int):
    """
    Retrieves a previously generated AI analysis report.
    """
    print(f"\n--- Fetching Report ID: {report_id} ---")
    endpoint = f"{BASE_URL}/reports/{report_id}"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        report = response.json()
        print("Report Retrieved Successfully:")
        print(json.dumps(report, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching report {report_id}: {e}")

def main():
    print("Starting AI Analysis Test Script...")
    print("Ensure your backend server is running at http://127.0.0.1:8000")
    print("You can also check the API documentation at http://127.0.0.1:8000/docs")

    # Test Ecosystem Analysis
    ecosystem_report_id = test_ecosystem_analysis()
    if ecosystem_report_id:
        # Give the backend some time to process the analysis
        print("\nWaiting for 5 seconds for report generation...")
        time.sleep(5)
        get_report(ecosystem_report_id)

    print("\n" + "="*50 + "\n")

    # Test Species Analysis
    species_report_id = test_species_analysis()
    if species_report_id:
        # Give the backend some time to process the analysis
        print("\nWaiting for 5 seconds for report generation...")
        time.sleep(5)
        get_report(species_report_id)

    print("\nAI Analysis Test Script Finished.")

if __name__ == "__main__":
    main()
