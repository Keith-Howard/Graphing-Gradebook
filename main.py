import matplotlib
import pandas as pd
import matplotlib.pyplot as plt


def create_dataframe_from_csv_file(csv_file):
    return pd.read_csv(csv_file)


def merge_quiz_grades(files):
    quiz_grades_dataframe = create_dataframe_from_csv_file(files[0])
    index = 1
    for file in files[1:]:
        quiz_grades_dataframe.rename(columns={'Grade': 'Quiz ' + str(index)}, inplace=True)
        new_df = create_dataframe_from_csv_file(file)
        quiz_grades_dataframe = pd.merge(quiz_grades_dataframe, new_df[['Last Name', 'First Name', 'Grade']],
                                         on=['Last Name', 'First Name'], how="left")
        index += 1
    quiz_grades_dataframe.rename(columns={'Grade': 'Quiz ' + str(index)}, inplace=True)
    return quiz_grades_dataframe


def create_name_column(dataframe):
    dataframe.loc[:, 'Name'] = dataframe['Last Name'] + ', ' + dataframe['First Name']


def add_quiz_max_points(dataframe):
    dataframe['Quiz 1 - Max Points'] = 11
    dataframe['Quiz 2 - Max Points'] = 15
    dataframe['Quiz 3 - Max Points'] = 17
    dataframe['Quiz 4 - Max Points'] = 14
    dataframe['Quiz 5 - Max Points'] = 12
    return dataframe


def create_gradebook_df(dataframes, columns_to_drop):
    grade_book_dataframe = dataframes[0]
    grade_book_dataframe['NetID_lower'] = grade_book_dataframe["NetID"].str.lower()
    grade_book_dataframe['Email Address_lower'] = grade_book_dataframe["Email Address"].str.lower()
    for dataframe in dataframes[1:]:
        if 'SID' in dataframe.columns:
            dataframe['SID_lower'] = dataframe['SID'].str.lower()
            grade_book_dataframe = pd.merge(grade_book_dataframe, dataframe, left_on='NetID_lower',
                                            right_on='SID_lower',
                                            how='left')
        else:
            dataframe['Email_lower'] = dataframe['Email'].str.lower()
            grade_book_dataframe = pd.merge(grade_book_dataframe, dataframe, left_on='Email Address_lower',
                                            right_on='Email_lower', how='left')
    grade_book_dataframe = grade_book_dataframe.drop(
        ['First Name_x', 'Last Name_x', 'ID', 'Last Name_y', 'First Name_y',
         'NetID', 'Email', 'Email Address', 'Section', 'Email Address_lower',
         'Name', 'Name_y', 'SID_lower', 'Email_lower'], axis=1)
    grade_book_dataframe = add_quiz_max_points(grade_book_dataframe)
    grade_book_dataframe = drop_homework_or_exam_sub_time_column(grade_book_dataframe, columns_to_drop)
    # grade_book_dataframe = drop_homework_or_exam_sub_time_column(grade_book_dataframe, 'Homework')
    grade_book_dataframe = set_nan_scores_to_zero(grade_book_dataframe, 'Exam')
    grade_book_dataframe = set_nan_scores_to_zero(grade_book_dataframe, 'Quiz')
    grade_book_dataframe = set_nan_scores_to_zero(grade_book_dataframe, 'Homework')
    return grade_book_dataframe


# drop_columns = [['Homework', '- Submission Time'], ['Exam', '- Submission Time']]
# pass a list of nested list with column labels in it
# first for loop iterates over the nested lists
# ['Homework', '- Submission Time']
#
# second for loop iterates over the items in the nested list
# 'Homework', '- Submission Time'
# if the label is in the dataframe drop the column

def drop_homework_or_exam_sub_time_column(dataframe, column_labels):
    for column in column_labels:
        begin_label = column[0]
        end_label = column[1]
        index = 1
        while True:
            search_label = begin_label + ' ' + str(index) + ' ' + end_label
            if search_label in dataframe:
                dataframe = dataframe.drop([search_label], axis=1)
                index += 1
            else:
                break
    return dataframe


def set_nan_scores_to_zero(dataframe, column_label):
    col_labels = {}
    index = 1
    while True:
        column = (column_label + ' ' + str(index))
        if column in dataframe:
            col_labels[column] = 0
        else:
            break
        index += 1
    return dataframe.fillna(value=col_labels)


# df["sum"] = df[['A', 'B', 'C']].sum(axis=1)
def calculate_quiz_and_homework_grade(dataframe, col_label):
    column_score_labels = []
    max_points_labels = []
    index = 1
    while True:
        if (col_label + ' ' + str(index)) in dataframe:
            column_score_labels.append(col_label + ' ' + str(index))
            if (col_label + ' ' + str(index) + ' - Max Points') in dataframe:
                max_points_labels.append(col_label + ' ' + str(index) + ' - Max Points')
        else:
            break
        index += 1
    dataframe[col_label + ' Grade'] = dataframe[column_score_labels].sum(axis=1) / dataframe[max_points_labels].sum(
        axis=1)
    return dataframe


def calculate_exam_grades(dataframe):
    index = 1
    while True:
        if ('Exam ' + str(index)) in dataframe:
            dataframe['Exam ' + str(index) + ' Grade'] = dataframe['Exam ' + str(index)] / \
                                                         dataframe['Exam ' + str(index) + ' - Max Points']
        else:
            break
        index += 1
    return dataframe


def calculate_number_grades(dataframe):
    dataframe['Final Number Grade'] = round(((dataframe['Exam 1 Grade'] * .05) + (dataframe['Exam 2 Grade'] * .10) +
                                             (dataframe['Exam 3 Grade'] * .15) + (dataframe['Quiz Grade'] * .30) +
                                             (dataframe['Homework Grade'] * .40)) * 100)
    return dataframe


def calculate_letter_grade(dataframe):
    if dataframe['Final Number Grade'] >= 90:
        grade = 'A'
    elif dataframe['Final Number Grade'] >= 80:
        grade = 'B'
    elif dataframe['Final Number Grade'] >= 70:
        grade = 'C'
    elif dataframe['Final Number Grade'] >= 60:
        grade = 'D'
    else:
        grade = 'F'
    return grade


def set_graph_characteristics(figure, axis_coordinates, x_values, y_values, bar_width, title, font_size):
    matplotlib.rcParams.update({'font.size': font_size})
    ax = figure.add_axes(axis_coordinates)
    ax.bar(x_values, y_values, width=bar_width)
    ax.set_title(title)


def get_values_by_category_column(dataframe, category_label):
    grade_counts = dataframe[category_label].value_counts()
    sorted_grade_count = grade_counts.sort_index()
    return sorted_grade_count.values


def list_of_dataframes(roster_file, homework_file, quiz_files):
    class_roster_df = create_dataframe_from_csv_file(roster_file)
    homework_and_exams_grades_df = create_dataframe_from_csv_file(homework_file)
    quiz_grades_df = merge_quiz_grades(quiz_files)
    create_name_column(homework_and_exams_grades_df)
    create_name_column(quiz_grades_df)
    return [class_roster_df, homework_and_exams_grades_df, quiz_grades_df]


# step 1 get input data into one merged df
class_roster = r'input/roster.csv'
homework_and_exams_grades = r'input/hw_exam_grades.csv'
quiz_1_grades = r'input/quiz_1_grades.csv'
quiz_2_grades = r'input/quiz_2_grades.csv'
quiz_3_grades = r'input/quiz_3_grades.csv'
quiz_4_grades = r'input/quiz_4_grades.csv'
quiz_5_grades = r'input/quiz_5_grades.csv'
quiz_grade_files = [quiz_1_grades, quiz_2_grades, quiz_3_grades, quiz_4_grades, quiz_5_grades]
drop_columns = [['Homework', '- Submission Time'], ['Exam', '- Submission Time']]
dataframes_to_merge = list_of_dataframes(class_roster, homework_and_exams_grades, quiz_grade_files)
gradebook_df = create_gradebook_df(dataframes_to_merge, drop_columns)
# calculate grade
gradebook_df = calculate_quiz_and_homework_grade(gradebook_df, 'Homework')
gradebook_df = calculate_quiz_and_homework_grade(gradebook_df, 'Quiz')
gradebook_df = calculate_exam_grades(gradebook_df)
gradebook_df = calculate_number_grades(gradebook_df)
gradebook_df['Final Letter Grade'] = gradebook_df.apply(calculate_letter_grade, axis=1)
# graph data
grade_labels = ['A', 'B', 'C', 'D', 'F']
gradebook_df['Final Letter Grade'] = pd.Categorical(gradebook_df['Final Letter Grade'],
                                                    categories=grade_labels, ordered=True)
fig = plt.figure('Final Grades Graph', figsize=(8, 5))
set_graph_characteristics(fig, [0.08, 0.10, 0.85, 0.75], grade_labels,
                          get_values_by_category_column(gradebook_df, 'Final Letter Grade'),
                          .45, 'Final Letter Grades\n', 9)
plt.xlabel('Grade')
plt.ylabel('# of Students')
plt.show()
x = 0
