from pathlib import Path
import pandas as pd
import numpy as np


HERE = Path(__file__).parent
DATA_FOLDER = HERE / "data"

roster = pd.read_csv(
	DATA_FOLDER / 'roster.csv',
	converters = {"NetID": str.lower, "Email Address":str.lower},
	usecols = ['NetID', 'Email Address', 'Section'],
	index_col = 'NetID'
	)
hw_exam_grades = pd.read_csv(
	DATA_FOLDER / 'hw_exam_grades.csv',
	converters = {"SID": str.lower},
	usecols = lambda x: "Submission" not in x,
	index_col = "SID"
	)

quiz_grades = pd.DataFrame()
for file in DATA_FOLDER.glob("quiz_*_grades.csv"):
	quiz_name = " ".join(file.stem.title().split("_")[: 2])
	quiz = pd.read_csv(
		file,
		converters= {"Email": str.lower},
		index_col= ['Email'],
		usecols=["Email", "Grade"],
		).rename(columns= {"Grade": quiz_name})
	quiz_grades = pd.concat([quiz_grades, quiz],axis= 1)

# 02 - MERGING DATAFRAMES
final_data = pd.merge(roster, hw_exam_grades, left_index= True, right_index= True)

final_data = pd.merge(
    final_data, quiz_grades, left_on="Email Address", right_index=True
)

final_data = final_data.fillna(0)

# calculating 
#1 calculating the exam total score

n_exams = 3
for i in range(1, n_exams + 1):
	final_data[f"Exam {i} score"] = (final_data[f'Exam {i}']  / final_data[f"Exam {i} - Max Points"])
# calculating the homework
homework_scores = final_data.filter(regex=r"^Homework \d\d?$", axis=1)
homework_max_points = final_data.filter(regex=r"^Homework \d\d? -", axis=1)

final_data['Sum of homework '] =  homework_scores.sum(axis = 1)
final_data['Sum of max_point '] = homework_max_points.sum(axis = 1)

final_data['Total homework'] = final_data['Sum of homework '] / final_data['Sum of max_point ']

hw_max_rename = homework_max_points.set_axis(homework_scores.columns, axis= 1)

average_hw_scores = (homework_scores / hw_max_rename).sum(axis= 1)

final_data['average_hw_scores'] = average_hw_scores / homework_scores.shape[1]

final_data["Homework Score"] = final_data[
    ["Total homework", "average_hw_scores"]
].max(axis=1)

# calculating quiz

quiz_scores = final_data.filter(regex=r"^Quiz \d$", axis=1)

quiz_max_points = pd.Series(
    {"Quiz 1": 11, "Quiz 2": 15, "Quiz 3": 17, "Quiz 4": 14, "Quiz 5": 12}
)

sum_of_quiz_scores = quiz_scores.sum(axis= 1)
sum_of_max_points = quiz_max_points.sum()
final_data['Total Quizzes'] = sum_of_quiz_scores / sum_of_max_points

average_quiz_score = (quiz_scores / quiz_max_points).sum(axis= 1)

final_data["average quizzes"] = average_quiz_score / quiz_scores.shape[1]

final_data["Quiz Score"] = final_data[
    ["Total Quizzes", "average quizzes"]
].max(axis=1)


weightings = pd.Series(
    {
        "Exam 1 score": 0.05,
        "Exam 2 score": 0.1,
        "Exam 3 score": 0.15,
        "Homework Score": 0.4,
        "Quiz Score": 0.30,
   
    }
)

final_data['Final score'] = (final_data[weightings.index] * weightings).sum(axis= 1)
final_data["Ceiling Score"] = np.ceil(final_data['Final score'] * 100)

grades = {
    90: "A",
    80: "B",
    70: "C",
    60: "D",
    0: "F",
}

def grade_mapping(value):
	for key, letter in grades.items():
		if value >= key:
			return letter


letter_grades = final_data['Ceiling Score'].map(grade_mapping)

