from components.degree_planner import run as degree_planner
from components.career_mentor import run as career_mentor
from components.skills_gap import run as skills_gap

def main():
    print("\n🎓 MSBA Smart Advisor")
    print("=" * 50)
    print("Select a component:")
    print("  1. Degree Planner")
    print("  2. Career Mentor")
    print("  3. Skills Gap Analyzer")
    print("  0. Exit")
    print("=" * 50)

    while True:
        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            degree_planner()
        elif choice == "2":
            career_mentor()
        elif choice == "3":
            skills_gap()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 0.")

if __name__ == "__main__":
    main()