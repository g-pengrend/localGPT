import sys
import json

from utils import (
    error,
    clean_json_string
)

def main():
    if len(sys.argv) != 2:
        error("Usage: python3 convert.py <answer>")
        sys.exit(1)

    answer = sys.argv[1]
    json_string = clean_json_string(answer)
    data = json.loads(json_string)
    

if __name__ == "__main__":
    main()