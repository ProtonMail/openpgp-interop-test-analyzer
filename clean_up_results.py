import sys
import json

"""
Read json from stdin, fix the category and write it to the stdout.
"""
def main():
    data = json.load(sys.stdin)
    data["results"] = [
        fix_category(category) for category in data["results"]
    ]
    data_fixed_json = json.dumps(data, indent=2)
    print(data_fixed_json)
    
def fix_category(category):
    return {"section": category[0], "results": category[1]}

if __name__ == "__main__":
    main()

