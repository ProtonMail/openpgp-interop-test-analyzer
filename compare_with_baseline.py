import sys
import json
from enum import Enum

def main():
    data = json.load(sys.stdin)
    (baseline, target) = get_args()
    all_changes = compare_with_baseline(data, baseline, target)
    json.dump(all_changes, sys.stdout, indent=2)

def compare_with_baseline(data, baseline, target):
    all_changes = []
    for section in data["results"]:
        section_results = section["results"]
        section_changes = []
        for test in section_results:
            test_runs = test["results"]
            producer_test_result_changes = check_target_producer_run(section, test, test_runs, baseline, target)
            consumer_test_result_changes = check_target_consumer_run(section, test, test_runs, baseline, target)
            test_result_changes = producer_test_result_changes + consumer_test_result_changes
            if test_result_changes is not None and len(test_result_changes) != 0:
                section_changes.append({"test": test["title"], "changes": test_result_changes})
        if section_changes is not None and len(section_changes) != 0:
            all_changes.append({"section": section["section"], "changes": section_changes})
    return all_changes

def check_target_consumer_run(section, test, test_runs, baseline, target):
    find_target = lambda test_result : test_result["producer"] == target
    find_baseline = lambda test_result : test_result["producer"] == baseline
    result_changes = []
    for test_run in test_runs:
        artifact_producer = test_run["artifact"]["producer"]
        if test_run["artifact"]["score"] != SUCCESS and test_run["artifact"]["score"] != NEUTRAL:
            continue
        target_result = find(test_run["results"], find_target)
        if target_result is None:
            print_err("Could not find target result: %s - %s - %s" % (section["section"], test["title"], artifact_producer))
            continue
        baseline_result = find(test_run["results"], find_baseline)
        if baseline_result is None:
            print_err("Could not find target result: %s - %s - %s" % (section["section"], test["title"], artifact_producer))
            continue
        result_change = compare_results(baseline_result, target_result)
        if result_change != ResultChange.UNCHANGED:
            result_changes.append(
                {
                    "producer": artifact_producer,
                    "consumer": target,
                    "change": result_change.to_string()
                }
            )
    return result_changes

def check_target_producer_run(section, test, test_runs, baseline, target):
    find_target = lambda test_run : test_run["artifact"]["producer"] == target
    find_baseline = lambda test_run : test_run["artifact"]["producer"] == baseline
    target_run = find(test_runs, find_target)
    if target_run is None:
        return []
    baseline_run = find(test_runs, find_baseline,)
    if baseline_run is None:
        print_err("Could not find baseline: %s - %s" % (section["section"], test["title"]))
        return []
    result_changes = []
    artifact_change = compare_results(baseline_run["artifact"], target_run["artifact"])
    if artifact_change != ResultChange.UNCHANGED:
        result_changes.append(
            {
                "producer": target,
                "consumer": "artifact",
                "change": artifact_change.to_string()
            }
        )
    for target_result in target_run["results"]:
        result_producer = target_result["producer"]
        find_baseline_result = lambda x: x["producer"] == result_producer
        baseline_result = find(baseline_run["results"], find_baseline_result)
        if baseline_result is None:
            print_err("Could not find baseline result: %s - %s - %s" % (section["section"], test["title"], result_producer), file=sys.stderr)
            continue
        result_change = compare_results(baseline_result, target_result)
        if result_change != ResultChange.UNCHANGED:
            result_changes.append(
                {
                    "producer": target,
                    "consumer": result_producer,
                    "change": result_change.to_string()
                }
            )
    return result_changes

class ResultChange(Enum):
    UNCHANGED = 0
    REGRESSION = 1
    IMPROVEMENT = 2
    
    def to_string(self):
        if self == ResultChange.UNCHANGED:
            return "Unchanged"
        elif self == ResultChange.REGRESSION:
           return "Regression"
        elif self == ResultChange.IMPROVEMENT:
            return "Improvement"
        else:
            return "Unknown"

NEUTRAL = "Neutral"
SUCCESS = "Success"
FAILURE = "Failure"
    

def compare_results(baseline_result, target_result):
    target_score = target_result["score"]
    baseline_score = baseline_result["score"]
    if baseline_score == target_score:
        return ResultChange.UNCHANGED
    elif target_score == FAILURE or (target_score == NEUTRAL and baseline_score == SUCCESS):
        return ResultChange.REGRESSION
    elif target_score == SUCCESS or (target_score == NEUTRAL and baseline_score == FAILURE):
        return ResultChange.IMPROVEMENT
    else:
        print_err("Unknown scores: %s - %s" % (baseline_score, target_score))
        return ResultChange.UNCHANGED

def print_err(value):
    print(value, file=sys.stderr)
        
def find(array, predicate):
    return next(
        filter(predicate, array),
        None
    )

def get_args():
    if len(sys.argv) != 3:
        sys.exit("Invalid arguments")
    baseline = sys.argv[1]
    target = sys.argv[2]
    return (baseline, target)
    
if __name__ == "__main__":
    main()