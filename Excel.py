import os
from statistics import mean, stdev

import pandas as pd
import xlsxwriter
import openpyxl
from datetime import datetime
import Settings as s
from Joint import Joint
import openpyxl
from openpyxl.drawing.image import Image
from openpyxl.chart import LineChart, Reference
import matplotlib.pyplot as plt
import io
import Settings as s
from xlsxwriter import Workbook



def create_workbook():
    datetime_string = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    workbook_name = f"{s.chosen_patient_ID} {datetime_string}.xlsx"
    s.excel_workbook_name = workbook_name
    s.excel_workbook = xlsxwriter.Workbook(workbook_name)
    create_Last_workbook()


def create_Last_workbook():
    file_path = f"{s.chosen_patient_ID}_Last.xlsx"

    try:
        # Load the existing workbook into a variable
        s.Last_workbook = openpyxl.load_workbook(file_path)

        # Check if "success" sheet exists, if not add it
        if "success" not in s.Last_workbook.sheetnames:
            s.Last_workbook.create_sheet("success")


        # Check if "effort" sheet exists, if not add it
        if "effort" not in s.Last_workbook.sheetnames:
            s.Last_workbook.create_sheet("effort")

        # Save the workbook after adding sheets
        s.Last_workbook.save(file_path)


    except FileNotFoundError:

        print(f"File '{file_path}' not found. Creating a new workbook.")

        # Create a new workbook
        s.Last_workbook = openpyxl.Workbook()

        # Remove the default sheet named "Sheet"
        default_sheet = s.Last_workbook["Sheet"]
        s.Last_workbook.remove(default_sheet)

        # Add "success" sheet
        s.Last_workbook.create_sheet("success")

        # Add "effort" sheet
        s.effort_sheet = s.Last_workbook.create_sheet("effort")


        s.Last_workbook.save(file_path)

    except Exception as e:
        print(f"An error occurred: {e}")





def get_success_number(exercise):
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(s.excel_file_path_Patient)

        # Check if the worksheet exists
        if "success" not in workbook.sheetnames:
            print(f"Worksheet success not found in the workbook.")
            return None

        # Select the worksheet
        worksheet = workbook["success"]

        # Iterate through the rows in the first column and search for the value
        for row in worksheet.iter_rows(values_only=True):
            if row[0] == exercise:
                # Return the value from the second column
                return row[1]

        # If the value is not found, return None
        return None

    except FileNotFoundError:
        print(f"File success not found.")
        return None



def get_effort_number(exercise):
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(s.excel_file_path_Patient)

        # Check if the worksheet exists
        if "success" not in workbook.sheetnames:
            print(f"Worksheet success not found in the workbook.")
            return None

        # Select the worksheet
        worksheet = workbook["effort"]

        # Iterate through the rows in the first column and search for the value
        for row in worksheet.iter_rows(values_only=True):
            if row[0] == exercise:
                # Return the value from the second column
                return row[1]

        # If the value is not found, return None
        return None

    except FileNotFoundError:
        print(f"File success not found.")
        return None


def wf_joints(ex_name, list_joints):
    if ex_name in s.Last_workbook.sheetnames:
        # Remove the existing sheet
        s.Last_workbook.remove(s.Last_workbook[ex_name])

    worksheet1 = s.excel_workbook.add_worksheet(ex_name)
    worksheet2 = s.Last_workbook.create_sheet(title=ex_name)
    col = 0

    for l in range(0, len(list_joints)):
        worksheet1.write(0, col, col + 1)
        worksheet2.cell(1, col+1, col + 1)

        row = 1
        for j in list_joints[l]:
            if isinstance(j, Joint):  # Check if j is a Joint object
                j_ar = j.joint_to_array()
                for i in range(len(j_ar)):
                    worksheet1.write(row, col, str(j_ar[i]))
                    worksheet2.cell(row+1, col+1, str(j_ar[i])) #index starts from 1
                    row += 1

            else:
                # Handle other types appropriately, e.g., just write the value to the worksheet
                worksheet1.write(row, col, str(j))
                worksheet2.cell(row+1, col+1, str(j))
                row += 1

        col += 1

    create_graphs(ex_name)


def create_graphs(exercise):

    try:
        df = pd.read_excel(s.excel_file_path_Patient, sheet_name=exercise)
        if get_number_of_angles_in_exercise(exercise) == 1:
            one_angle_graph(df, exercise)
        if get_number_of_angles_in_exercise(exercise) == 2:
            two_angles_graph(df, exercise)
        if get_number_of_angles_in_exercise(exercise) == 3:
            three_angles_graph(df, exercise)


    except (pd.errors.ParserError, FileNotFoundError):
        # Handle the case where the sheet is not found
        pass  # Continue to the next iteration
    except ValueError as ve:
        # Handle other specific errors
        pass  # Continue to the next iteration



def get_number_of_angles_in_exercise(exercise):
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook("exercises_table.xlsx")

        # Select the desired sheet
        sheet = workbook[workbook.sheetnames[0]]

        # Iterate through rows starting from the specified row
        for row_number in range(1, sheet.max_row + 1):
            first_cell_value = sheet.cell(row=row_number, column=1).value

            if first_cell_value == exercise:
                return sheet.cell(row=row_number, column=2).value


    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def three_angles_graph(df, exercise):
    worksheet = s.excel_workbook.add_worksheet(("graphs_"+exercise)[:31])

    first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
    y_values_1 = df.iloc[72, :]
    y_values_1_float = y_values_1.astype(float)
    create_and_save_graph(df.columns, y_values_1_float, first_graph_name, worksheet, 72)

    second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
    y_values_2 = df.iloc[73, :]
    y_values_2_float = y_values_2.astype(float)
    create_and_save_graph(df.columns, y_values_2_float, second_graph_name, worksheet, 73)

    third_graph_name = df.iloc[24, 0] + ", " + df.iloc[28, 0] + ", " + df.iloc[32, 0]
    y_values_3 = df.iloc[74, :]
    y_values_3_float = y_values_3.astype(float)
    create_and_save_graph(df.columns, y_values_3_float, third_graph_name, worksheet, 74)

    fourth_graph_name = df.iloc[36, 0] + ", " + df.iloc[40, 0] + ", " + df.iloc[44, 0]
    y_values_4 = df.iloc[75, :]
    y_values_4_float = y_values_4.astype(float)
    create_and_save_graph(df.columns, y_values_4_float, fourth_graph_name, worksheet, 75)

    fifth_graph_name = df.iloc[48, 0] + ", " + df.iloc[52, 0] + ", " + df.iloc[56, 0]
    y_values_5 = df.iloc[76, :]
    y_values_5_float = y_values_5.astype(float)
    create_and_save_graph(df.columns, y_values_5_float, fifth_graph_name, worksheet, 76)

    sixth_graph_name = df.iloc[60, 0] + ", " + df.iloc[64, 0] + ", " + df.iloc[68, 0]
    y_values_6 = df.iloc[77, :]
    y_values_6_float = y_values_6.astype(float)
    create_and_save_graph(df.columns, y_values_6_float, sixth_graph_name, worksheet, 77)

def two_angles_graph(df, exercise):
    worksheet = s.excel_workbook.add_worksheet(("graphs_"+exercise)[:31])

    first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
    y_values_1 = df.iloc[48, :]
    y_values_1_float = y_values_1.astype(float)
    create_and_save_graph(df.columns, y_values_1_float, first_graph_name, worksheet, 48)

    second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
    y_values_2 = df.iloc[49, :]
    y_values_2_float = y_values_2.astype(float)
    create_and_save_graph(df.columns, y_values_2_float, second_graph_name, worksheet, 49)

    third_graph_name = df.iloc[24, 0] + ", " + df.iloc[28, 0] + ", " + df.iloc[32, 0]
    y_values_3 = df.iloc[50, :]
    y_values_3_float = y_values_3.astype(float)
    create_and_save_graph(df.columns, y_values_3_float, third_graph_name, worksheet, 50)

    fourth_graph_name = df.iloc[36, 0] + ", " + df.iloc[40, 0] + ", " + df.iloc[44, 0]
    y_values_4 = df.iloc[51, :]
    y_values_4_float = y_values_4.astype(float)
    create_and_save_graph(df.columns, y_values_4_float, fourth_graph_name, worksheet, 51)

def one_angle_graph(df, exercise):
    worksheet = s.excel_workbook.add_worksheet(("graphs_"+exercise)[:31])

    first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
    y_values_1 = df.iloc[24, :]
    y_values_1_float = y_values_1.astype(float)
    create_and_save_graph(df.columns, y_values_1_float, first_graph_name, worksheet, 24)

    second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
    y_values_2 = df.iloc[25, :]
    y_values_2_float = y_values_2.astype(float)
    create_and_save_graph(df.columns, y_values_2_float, second_graph_name, worksheet, 25)

def create_and_save_graph(x_values, y_values, graph_name, worksheet, row_of_values):
    # Write the x and y data to the worksheet.
    worksheet.write_row('A1', x_values)
    worksheet.write_row('A2', y_values)

    # Create a new chart object.
    chart = s.excel_workbook.add_chart({'type': 'line'})

    last_column_letter = chr(ord('A') + len(x_values) - 1)  # Convert the length to a column letter

    # Add series with x and y values.
    chart.add_series({
        'name': graph_name,  # Title of the series
        'categories': f'={worksheet.name}!$A$1:${last_column_letter}$1',  # X values
        'values': f'={worksheet.name}!$A$2:${last_column_letter}${row_of_values}'  # Y values
    })

    # Add title to the chart
    chart.set_title({'name': graph_name})

    # Add axis labels
    chart.set_x_axis({'name': 'מספר מדידה'})
    chart.set_y_axis({'name': 'זווית'})

    # Insert the chart into the worksheet.
    worksheet.insert_chart('D'+str(row_of_values), chart)




def success_worksheet():
    s.success_sheet = s.excel_workbook.add_worksheet("success")
    s.success_sheet.write(0, 0, "exercise")
    s.success_sheet.write(0, 1, "number of successful repetitions")

    row = 1
    for exercise, success in s.ex_list.items():
        s.success_sheet.write(row, 0, exercise)
        s.success_sheet.write(row, 1, success)

        row += 1

    find_and_change_values_success_in_Last()

def effort_worksheet():
    s.effort_sheet = s.excel_workbook.add_worksheet("effort")
    s.effort_sheet.write(0, 0, "exercise")
    s.effort_sheet.write(0, 1, "effort")

    row = 1
    for exercise, effort in s.list_effort_each_exercise.items():
        s.effort_sheet.write(row, 0, exercise)
        s.effort_sheet.write(row, 1, effort)

        row += 1

    find_and_change_values_effort_in_Last()

def find_and_change_values_Patients(new_values_dict, headers_row=1):
    # Load the workbook
    file_path = "Patients.xlsx"
    workbook = openpyxl.load_workbook(file_path)

    # Select the desired sheet
    sheet = workbook["patient_details_and_exercises"]

    # Find the column indices based on the header names
    column_indices = {}
    for header_name, new_value in new_values_dict.items():
        for cell in sheet[headers_row]:
            if cell.value == header_name:
                column_indices[header_name] = cell.column
                break

    # Iterate through the rows to find the value in the first column
    for row in sheet.iter_rows(min_row=headers_row + 1, max_row=sheet.max_row, min_col=1, max_col=1):
        cell = row[0]
        if str(cell.value) == s.chosen_patient_ID:
            # Update the values in the corresponding columns
            for header_name, column_index in column_indices.items():
                sheet.cell(row=cell.row, column=column_index, value=new_values_dict[header_name])

    # Save the changes
    workbook.save(file_path)


def find_and_add_training_to_patient(headers_row=1):
    # Load the workbook
    file_path = "Patients.xlsx"
    workbook = openpyxl.load_workbook(file_path)

    # Select the desired sheet
    sheet = workbook["patients_history_of_trainings"]

    # Iterate through the rows to find the value in the first column
    for row in sheet.iter_rows(min_row=headers_row + 1, max_row=sheet.max_row, min_col=1, max_col=1):
        cell = row[0]
        if str(cell.value) == s.chosen_patient_ID:
            # Find the next available column in the row
            next_column = sheet.max_column + 1

            # Write the new value to the next available column in the row
            sheet.cell(row=cell.row, column=next_column, value=s.excel_workbook_name)
            break  # Stop searching after finding the value

    workbook.save(file_path)



def find_and_change_values_effort_in_Last(headers_row=1):
    # Select the desired sheet
    sheet = s.Last_workbook["effort"]
    new_values_dict = s.list_effort_each_exercise

    # Get all the keys (exercise names) from the new_values_dict
    #search_values = list(new_values_dict.keys())

    # Check if the sheet is empty (contains only headers)
    if sheet.max_row == headers_row:
        # Add headers
        sheet.cell(row=headers_row, column=1, value="exercise")
        sheet.cell(row=headers_row, column=2, value="effort")

    # Iterate over new_values_dict
    for exercise_name, effort_number in new_values_dict.items():
        found = False
        # Iterate through the existing rows to check if the exercise is already in the sheet
        for row in sheet.iter_rows(min_row=headers_row + 1, max_row=sheet.max_row, min_col=1, max_col=2):
            if row[0].value == exercise_name:
                found = True
                # Update the value in the second column
                row[1].value = effort_number
                break

        # If the exercise is not found in the sheet, add it as a new row
        if not found:
            new_row_index = sheet.max_row + 1
            sheet.cell(row=new_row_index, column=1, value=exercise_name)
            sheet.cell(row=new_row_index, column=2, value=effort_number)


def find_and_change_values_success_in_Last(headers_row=1):
    # Select the desired sheet
    sheet = s.Last_workbook["success"]
    new_values_dict = s.ex_list

    # Get all the keys (exercise names) from the new_values_dict
    #search_values = list(new_values_dict.keys())

    # Check if the sheet is empty (contains only headers)
    if sheet.max_row == headers_row:
        # Add headers
        sheet.cell(row=headers_row, column=1, value="exercise")
        sheet.cell(row=headers_row, column=2, value="number of successful repetitions")

    # Iterate over new_values_dict
    for exercise_name, success_count in new_values_dict.items():
        found = False
        # Iterate through the existing rows to check if the exercise is already in the sheet
        for row in sheet.iter_rows(min_row=headers_row + 1, max_row=sheet.max_row, min_col=1, max_col=2):
            if row[0].value == exercise_name:
                found = True
                # Update the value in the second column
                row[1].value = success_count
                break

        # If the exercise is not found in the sheet, add it as a new row
        if not found:
            new_row_index = sheet.max_row + 1
            sheet.cell(row=new_row_index, column=1, value=exercise_name)
            sheet.cell(row=new_row_index, column=2, value=success_count)




def close_workbook():
    s.Last_workbook.save(f"{s.chosen_patient_ID}_Last.xlsx")
    s.excel_workbook.close()





if __name__ == "__main__":
    s.chosen_patient_ID="315454"
    create_workbook()
    worksheet = s.excel_workbook.add_worksheet(("graphs_1")[:31])

    x_values=(1,2,3,4)
    y_values=(1,2,3,4)
    create_and_save_graph(x_values, y_values, "xxx", worksheet, 2)
    s.excel_workbook.close()


    def extract_string_between_spaces(input_string):
        parts = input_string.split()  # Split the string into parts based on spaces
        if len(parts) >= 3:  # Ensure there are at least three parts (two spaces)
            return parts[1]  # Extract the second part
        else:
            return None

    s.chosen_patient_ID='314808981'
    # Example usage:
    input_str = "315454 09-04-2024 13-42-08"
    result = extract_string_between_spaces(input_str)
    print(result)  # Output: "is"

    find_and_add_training_to_patient()