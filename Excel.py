import pandas as pd
import xlsxwriter
from datetime import datetime
from Joint import Joint
import openpyxl
import Settings as s
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import matplotlib.pyplot as plt
import numpy as np
from openpyxl.drawing.image import Image as XLImage
import Excel



def create_workbook():
    datetime_string = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    workbook_name = f"{s.chosen_patient_ID} {datetime_string}.xlsx"
    s.excel_workbook_name = workbook_name
    s.excel_workbook = xlsxwriter.Workbook(workbook_name)



def find_row_by_value(workbook_path, worksheet_name, ID, target_col):
    try:
        # Load the workbook
        workbook = load_workbook(workbook_path)

        # Access the worksheet
        worksheet = workbook[worksheet_name]
        target_row=None

        # Search for the target value in the first column
        for row_number, row in enumerate(worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=1, max_col=1), start=2):
            for cell in row:
                if str(cell.value) == ID:
                    target_row= row_number  # Return row number and value from specified column
                    break
            if target_row is not None:
                break

        for col in worksheet.iter_cols():
            # Check if the first cell in the column matches the specified column name
            if col[0].value == target_col:
                # Return the entire column
                return col[target_row-1].value

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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
    #if ex_name in s.Last_workbook.sheetnames:
        # Remove the existing sheet
     #   s.Last_workbook.remove(s.Last_workbook[ex_name])

    worksheet1 = s.excel_workbook.add_worksheet(ex_name)
    #worksheet2 = s.Last_workbook.create_sheet(title=ex_name)
    col = 0

    for l in range(0, len(list_joints)):
        worksheet1.write(0, col, col + 1)
        #worksheet2.cell(1, col+1, col + 1)

        row = 1
        for j in list_joints[l]:
            if isinstance(j, Joint):  # Check if j is a Joint object
                j_ar = j.joint_to_array()
                for i in range(len(j_ar)):
                    worksheet1.write(row, col, str(j_ar[i]))
                    #worksheet2.cell(row+1, col+1, str(j_ar[i])) #index starts from 1
                    row += 1

            else:
                # Handle other types appropriately, e.g., just write the value to the worksheet
                worksheet1.write(row, col, str(j))
                #worksheet2.cell(row+1, col+1, str(j))
                row += 1

        col += 1

    create_graphs(ex_name)


def create_graphs(exercise):

    try:
        df = pd.read_excel(s.excel_file_path_Patient, sheet_name=exercise)
        if get_number_of_angles_in_exercise(exercise) == 1:
            one_angle_graph(df, exercise)
       # if get_number_of_angles_in_exercise(exercise) == 2:
        #    two_angles_graph(df, exercise)
        #if get_number_of_angles_in_exercise(exercise) == 3:
         #   three_angles_graph(df, exercise)


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

def one_angle_graph(df, exercise):
    worksheet_graphs = s.excel_workbook.add_worksheet(("graphs_"+exercise)[:31])

    first_graph_name = df.iloc[0, 0] + ", " + df.iloc[4, 0] + ", " + df.iloc[8, 0]
    y_values_1 = df.iloc[24, :]
    y_values_1_float = y_values_1.astype(float)
    create_and_save_graph(df.columns, y_values_1_float, first_graph_name, worksheet_graphs, 24)

    second_graph_name = df.iloc[12, 0] + ", " + df.iloc[16, 0] + ", " + df.iloc[20, 0]
    y_values_2 = df.iloc[25, :]
    y_values_2_float = y_values_2.astype(float)
    create_and_save_graph(df.columns, y_values_2_float, second_graph_name, worksheet_graphs, 25)

    data = {
    first_graph_name: {'x': df.columns, 'y': y_values_1_float},
    second_graph_name: {'x': df.columns, 'y': y_values_2_float}}

    create_and_save_graph(data, worksheet_graphs)

def create_and_save_graph(data, worksheet_graphs):
    # Define the starting row and column for inserting the graphs
    start_row = 1

    # Iterate over each plot data
    for plot_name, plot_data in data.items():
        # Create a new plot
        plt.plot(plot_data['x'], plot_data['y'])
        plt.xlabel('מספר מדידה')
        plt.ylabel('זווית')
        plt.title(plot_name)

        # Add text box with statistics
        min_val = min(plot_data['y'])
        max_val = max(plot_data['y'])
        average = sum(plot_data['y']) / len(plot_data['y'])
        stdev = np.std(plot_data['y'])

        text_content = f" {min_val}מינימום: \n {max_val} מקסימום: \n  {round(average, 2)} ממוצע: \n {round(stdev,2)} סטיית תקן:"
        plt.text(0.95, 0.95, text_content, transform=plt.gca().transAxes, verticalalignment='top',
                 horizontalalignment='right', fontsize=7, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Save the plot as an image file
        plot_filename = f'temp_graph.png'
        plt.savefig(plot_filename)
        plt.close()  # Close the plot to clear the figure


        worksheet_graphs.insert_image(f"A{start_row}", plot_filename)

        # Update the starting row for the next image
        start_row += 20  # Adjust as needed




def success_worksheet():
    s.success_sheet = s.excel_workbook.add_worksheet("success")
    s.success_sheet.write(0, 0, "exercise")
    s.success_sheet.write(0, 1, "number of successful repetitions")

    row = 1
    for exercise, success in s.ex_list.items():
        s.success_sheet.write(row, 0, exercise)
        s.success_sheet.write(row, 1, success)

        row += 1


    #find_and_change_values_success_in_Last()

def effort_worksheet():
    s.effort_sheet = s.excel_workbook.add_worksheet("effort")
    s.effort_sheet.write(0, 0, "exercise")
    s.effort_sheet.write(0, 1, "effort")

    row = 1
    for exercise, effort in s.list_effort_each_exercise.items():
        s.effort_sheet.write(row, 0, exercise)
        s.effort_sheet.write(row, 1, effort)

        row += 1

    #find_and_change_values_effort_in_Last()

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
            sheet.cell(row=cell.row, column=next_column, value=s.excel_workbook_name.replace(".xlsx", ""))
            sheet.cell(row=cell.row, column=next_column+1, value=(s.number_of_repetitions_in_training/s.max_repetitions_in_training))

            break  # Stop searching after finding the value

    workbook.save(file_path)


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
            sheet.cell(row=cell.row, column=next_column, value=s.excel_workbook_name.replace(".xlsx", ""))
            sheet.cell(row=cell.row, column=next_column+1, value=(s.number_of_repetitions_in_training/s.max_repetitions_in_training))

            break  # Stop searching after finding the value


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


def count_true_values_in_row_by_ID():
    # Select the specific sheet
    workbook = openpyxl.load_workbook("C:/Users/yaels/יעל פרוייקט גמר/zedcheck/Patients.xlsx")

    sheet = workbook["patient_details_and_exercises"]

    # Search for the row containing the search_value in the first column
    for row in sheet.iter_rows():
        if str(row[0].value) == s.chosen_patient_ID:
            row_number = row[0].row
            break
    else:
        # If the value is not found, return 0
        return 0

    # Get the values of the found row
    row_values = sheet[row_number]

    # Count the number of TRUE values in the row
    true_count = sum(1 for cell in row_values if cell.value is True)

    return true_count



def close_workbook():
    #s.Last_workbook.save(f"{s.chosen_patient_ID}_Last.xlsx")
    s.excel_workbook.close()


def extract_string_between_spaces(input_string):
    parts = input_string.split()  # Split the string into parts based on spaces
    if len(parts) >= 3:  # Ensure there are at least three parts (two spaces)
        return parts[1]  # Extract the second part
    else:
        return None



if __name__ == "__main__":


    find_row_by_value("314808981", "email")

    s.chosen_patient_ID="315454"
    create_workbook()
    s.excel_workbook.add_worksheet("graphs_1")

    worksheet = s.excel_workbook.get_worksheet_by_name("graphs_1")

    x_values=(1,2,3,4)
    y_values=(5,6,7,8)
    data = {
        "graph_1":{'x': x_values, 'y': y_values}}


    create_and_save_graph(data, worksheet)
    s.excel_workbook.close()




    s.chosen_patient_ID='314808981'
    # Example usage:
    input_str = "315454 09-04-2024 13-42-08"
    result = extract_string_between_spaces(input_str)
    print(result)  # Output: "is"

    find_and_add_training_to_patient()