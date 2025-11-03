import json
import argparse
import sys
from support_agent.core import get_answer, print_highlighted_json

parser = argparse.ArgumentParser(description="Run support-agent query and print JSON response + metrics.")
parser.add_argument("query", nargs=1, help="User question")
parser.add_argument("--metrics", action="store_true", help="Print metrics")

def main():
	# Try to parse args and on failure print a nicely formatted help message
	try:
		args = parser.parse_args()
	except SystemExit:
		# argparse already prints an error to stderr; show full help for clarity
		parser.print_help()
		sys.exit(2)

	answer, metrics = get_answer(args.query[0])
	print("Answer:\n-------\n") 
	print_highlighted_json(json.loads(answer))
	if args.metrics:
		print("\nMetrics:\n-------\n")
		print_highlighted_json(metrics)

if __name__ == "__main__":
	main()
