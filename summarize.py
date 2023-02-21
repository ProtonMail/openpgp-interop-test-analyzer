import sys
import json

def main():
    data = json.load(sys.stdin)
    summarize(data)

REGRESSION = "Regression"
IMPROVEMENT = "Improvement"

def summarize(data):
    regression = 0
    improvement = 0
    for section in data:
        for test in section["changes"] :
            for run in test["changes"] :
                if run["change"] == REGRESSION:
                    regression += 1
                elif run["change"] == IMPROVEMENT:
                    improvement += 1
                else:
                    print("Unknown change type %s" % run["change"], file=sys.stderr)
    regression_summary = plural(regression, "regression")
    improvement_summary = plural(improvement, "improvement")
    summary = "Summary: {}, {}".format(regression_summary, improvement_summary)
    print(summary)

def plural(value, name):
    if value != 1:
        name += "s"
    return "{} {}".format(value, name)

if __name__ == "__main__":
    main()