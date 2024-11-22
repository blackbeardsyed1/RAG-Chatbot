import pandas as pd

df = pd.read_csv('Internal_Record_FA17_to_FA20_csv_1.csv')

# df.rename(columns={'Obtained\n_Marks':'ObtainedMarks'}, inplace=True)
fall_2017_assignments_quizzes_check = df[(df['Session'] == 'Fall 2017') & (df['ExamType'].str.contains('Assign|Quiz', case=False))]
print(fall_2017_assignments_quizzes_check)
# print(df['Session'].value_counts())
# print(df[['Session','ExamType','ObtainedMarks']])
# print(df[df['ExamType'].str.contains('Assign|Quiz', case=False)])
# df['ExamType'] = df['ExamType'].str.strip()  # Remove leading/trailing spaces
# df['ExamType'] = df['ExamType'].str.replace(r'\s+', '', regex=True)
# fall_2017_assignments_quizzes_check = df[
#     (df['Session'] == 'Fall 2017') &
#     (df['ExamType'].str.contains('Assign', case=False, na=False))
# ]
# print(fall_2017_assignments_quizzes_check)
print(df['Session'].unique())
df['Session'] = df['Session'].str.strip()
print(df['Session'].unique())
fall_2017_df = df[df['Session'] == 'Fall 2017']

# Identify assignment and quiz types
assignment_quiz_types = ['Assign1', 'Assign2', 'Quiz1', 'Quiz2', 'Quiz3']
assignments_quizzes_df = fall_2017_df[fall_2017_df['ExamType'].isin(assignment_quiz_types)]

# Calculate average obtained marks for each type
average_obtained_marks = assignments_quizzes_df.groupby('ExamType')['ObtainedMarks'].mean()
print(average_obtained_marks)
# Find the lowest average
lowest_average = average_obtained_marks.min()
print(lowest_average)
# df.to_csv('Internal_Record_FA21_to_FA23_csv_1.csv',index=False)
# df.to_csv('Internal_Record_FA14_to_SP17_csv_1.csv',index=False)



