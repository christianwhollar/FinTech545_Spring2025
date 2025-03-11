import pandas as pd
from src.problem_one import problem_one
from src.problem_two import problem_two
from src.problem_three import problem_three

if __name__ == "__main__":
    df = pd.read_csv("./DailyPrices.csv")
    problem_one(df)
    problem_two(df)
    problem_three()