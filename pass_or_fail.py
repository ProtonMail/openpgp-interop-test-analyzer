import sys
import json

def main():
    data = json.load(sys.stdin)
    if has_regression(data) :
        sys.exit("Found a regression")

REGRESSION = "Regression"

def has_regression(data):
    for section in data:
        for test in section["changes"] :
            for run in test["changes"] :
                if run["change"] == REGRESSION:
                    return True
    return False

if __name__ == "__main__":
    main()