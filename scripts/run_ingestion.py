import argparse
import sys
from datetime import datetime

# Since we are running this as a module from the root, we can use absolute imports
from scripts.data_ingestion.nasa_ingester import NASAIngester
from scripts.data_ingestion.gbif_ingester import GBIFIngester
from scripts.data_ingestion.noaa_ingester import NOAAIngester

def run_nasa_ingestion():
    """Runs the NASA data ingestion process."""
    print("\n--- Ingesting NASA Climate Data ---")
    try:
        ingester = NASAIngester()
        ingester.ingest()
        print("--- NASA Ingestion Completed ---")
    except Exception as e:
        print(f"NASA Ingestion Failed: {e}", file=sys.stderr)

def run_gbif_ingestion(species: list[str], limit: int):
    """Runs the GBIF data ingestion process."""
    print(f"\n--- Ingesting GBIF Wildlife Data for {len(species)} species ---")
    try:
        ingester = GBIFIngester()
        ingester.ingest(species, limit_per_species=limit)
        print("--- GBIF Ingestion Completed ---")
    except Exception as e:
        print(f"GBIF Ingestion Failed: {e}", file=sys.stderr)

def run_noaa_ingestion(start_year: int, end_year: int, stations: list[str]):
    """Runs the NOAA data ingestion process."""
    print(f"\n--- Ingesting NOAA Climate Data for stations {stations} ---")
    try:
        ingester = NOAAIngester()
        ingester.ingest(start_year, end_year, station_ids=stations)
        print("--- NOAA Ingestion Completed ---")
    except Exception as e:
        print(f"NOAA Ingestion Failed: {e}", file=sys.stderr)

def main():
    """Main function to parse arguments and run selected data ingestion scripts."""
    parser = argparse.ArgumentParser(description="Run data ingestion scripts for the Climate Wildlife AI project.")
    parser.add_argument(
        'ingesters',
        nargs='+',
        choices=['nasa', 'gbif', 'noaa', 'all'],
        help="Specify which ingester(s) to run. Use 'all' to run them all."
    )
    
    # GBIF arguments
    parser.add_argument('--species', nargs='*', default=['Ursus maritimus', 'Panthera leo'], help='List of scientific names for GBIF ingestion.')
    parser.add_argument('--limit', type=int, default=200, help='Limit of occurrences per species for GBIF.')

    # NOAA arguments
    current_year = datetime.now().year
    parser.add_argument('--start_year', type=int, default=current_year - 3, help='Start year for NOAA ingestion.')
    parser.add_argument('--end_year', type=int, default=current_year - 1, help='End year for NOAA ingestion.')
    parser.add_argument('--stations', nargs='*', default=['GHCND:USW00014733'], help='List of NOAA station IDs.')

    args = parser.parse_args()

    print("--- Starting Full Data Ingestion Process ---")

    ingesters_to_run = args.ingesters
    if 'all' in ingesters_to_run:
        ingesters_to_run = ['nasa', 'gbif', 'noaa']

    if 'nasa' in ingesters_to_run:
        run_nasa_ingestion()
    
    if 'gbif' in ingesters_to_run:
        run_gbif_ingestion(args.species, args.limit)

    if 'noaa' in ingesters_to_run:
        run_noaa_ingestion(args.start_year, args.end_year, args.stations)

    print("\n--- Full Data Ingestion Process Completed ---")

if __name__ == "__main__":
    # To run this script, use the command:
    # python -m scripts.run_ingestion <ingester_name> [options]
    # Example: python -m scripts.run_ingestion all
    # Example: python -m scripts.run_ingestion gbif --species "Chelonia mydas" "Salmo salar" --limit 100
    # Example: python -m scripts.run_ingestion noaa --start_year 2020 --end_year 2022 --stations "GHCND:UK000003772"
    main()
