from pathlib import Path
import pandas as pd


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
print(quiz_grades)
