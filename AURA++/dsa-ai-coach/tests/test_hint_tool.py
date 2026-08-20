from tools import HintTool


def main():

    tool = HintTool()

    print("\n" + "=" * 60)
    print("HINT TOOL TEST")
    print("=" * 60)

    problem_ids = [
        "dp_001",
        "dp_002",
        "dp_003",
        "arr_001",
        "str_001"
    ]

    for problem_id in problem_ids:

        print(
            "\n" + "-" * 60
        )

        print(
            f"Problem ID: {problem_id}"
        )

        for level in range(1, 4):

            hint = tool.execute(
                problem_id=problem_id,
                hint_level=level
            )

            print(hint)


if __name__ == "__main__":
    main()