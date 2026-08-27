"""
NER-SAGE — SIH Demo Scenario Runner
Simulates the 11-step terminal output for the SIH presentation.
"""

import sys
import time


def print_step(title, data):
    print(f"\n\033[1;36m[STEP] {title}\033[0m")
    for key, val in data.items():
        print(f"  \033[1;33m{key}:\033[0m {val}")
    time.sleep(1.5)

def type_effect(text):
    print("\n\033[1;32mNER-SAGE AI > \033[0m", end="")
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)
    print("\n")
    time.sleep(1)

def run_demo():
    print("\n" + "="*50)
    print("\033[1;35m 🏔️  NER-SAGE: Self-Adaptive Geospatial Emergency Intelligence\033[0m")
    print("="*50)
    time.sleep(1)

    print_step("Initial Prediction (Road B)", {
        "Risk": "82% (HIGH)",
        "Confidence": "54% (LOW)",
    })

    print_step("Uncertainty Engine Analysis", {
        "Satellite": "STALE (9 days old)",
        "Ground Evidence": "MISSING",
        "Overall Evidence Status": "CONFLICTING"
    })

    type_effect("Risk is 82%, but confidence is low. I need to verify this.")

    print_step("Next-Best-Evidence Engine", {
        "Action Evaluated": "Verify Road B",
        "Decision Value": "0.92 (VERY HIGH)",
        "Reason": "High consequence area, ground truth is unknown."
    })

    type_effect("Requesting citizen verification or field report for Road B...")

    print_step("Human Evidence Arrives (Citizen Report #184)", {
        "Observation": "Partial debris blocking road. Fresh cracks visible. Water seepage.",
        "Computer Vision": "Cracks Detected (91% confidence)",
        "Reliability Score": "0.91"
    })

    print_step("Belief Update", {
        "Risk": "88% (HIGH)  [↑ +6%]",
        "Confidence": "91% (HIGH)  [↑ +37%]",
    })

    print_step("Consequence Engine (Neo4j Graph Analysis)", {
        "Road Blockage": "HIGH (76% probability)",
        "Village X Isolation": "HIGH (64% probability)",
        "Hospital Z Access": "DEGRADED"
    })

    type_effect("If Road B fails, 850 people in Village X will be isolated.")

    print_step("What-If Simulation (Rainfall +25%)", {
        "Simulated Risk": "94% (EXTREME)",
        "Simulated Isolation": "84% (VERY HIGH)"
    })

    print_step("Decision Engine Recommendation", {
        "1.": "Inspect Road B",
        "2.": "Prepare Route C",
        "3.": "Pre-position response team at Junction Y",
        "Approval": "Requires Human Authorization"
    })

    print("\n\033[1;31mHUMAN OPERATOR INPUT required [APPROVE/REJECT/MODIFY]:\033[0m APPROVE")
    time.sleep(1)

    type_effect("Decision recorded. Actions dispatched. Audit log updated.")

    print("\n" + "="*50)
    print("\033[1;35m DEMO COMPLETE\033[0m")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_demo()
