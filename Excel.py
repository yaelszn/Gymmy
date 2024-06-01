import pandas as pd
import xlsxwriter
from datetime import datetime
from Joint import Joint
import openpyxl
import Settings as s
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
import platform
import re



def create_and_open_folder(folder_path):
    try:
        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)
        print(f"Directory created or already exists: {folder_path}")

        # Check if the folder exists after creation
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Directory still not found: {folder_path}")

    except Exception as e:
        print(f"An error occurred: {e}")




#creats a new workbook to each training
def create_workbook():
    datetime_string = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    workbook_name = f"Patients/{s.chosen_patient_ID}/{datetime_string}.xlsx"
    s.training_workbook_path = workbook_name
    s.training_workbook_name= f"{datetime_string}.xlsx"
    s.training_workbook = xlsxwriter.Workbook(workbook_name)
    #s.training_workbook.save()




#returns a specific value by ID and name of the column
def find_value_by_colName_and_userID(workbook_path, worksheet_name, ID, target_col):
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


#returns the value of success in a specific training and specific exercise
def get_success_number(file_path, exercise):
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(file_path)

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


#returns the value of effort rate in a specific training and specific exercise
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
    worksheet1 = s.training_workbook.add_worksheet(ex_name[:31])
    col = 0

    for l in range(0, len(list_joints)):
        worksheet1.write(0, col, col + 1)

        row = 1
        for j in list_joints[l]:
            if isinstance(j, Joint):  # Check if j is a Joint object
                j_ar = j.joint_to_array()
                for i in range(len(j_ar)):
                    worksheet1.write(row, col, str(j_ar[i]))
                    row += 1

            else:
                # Handle other types appropriately, e.g., just write the value to the worksheet
                worksheet1.write(row, col, str(j))
                row += 1

        col += 1

    #s.training_workbook.save(s.training_workbook_path) #save the workbook
    create_graphs(ex_name, list_joints)


def create_graphs(exercise, list_joints):

    try:
        if get_number_of_angles_in_exercise(exercise) == 1:
            one_angle_graph(exercise, list_joints)
        if get_number_of_angles_in_exercise(exercise) == 2:
            two_angles_graph(exercise, list_joints)
        if get_number_of_angles_in_exercise(exercise) == 3:
            three_angles_graph(exercise, list_joints)


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

def one_angle_graph(exercise_name, list_joints):
    last_two_values = [entry[-2:] for entry in list_joints] #extract from each record the last 2 values (the angles)
    right_angles = [sublist[0] for sublist in last_two_values] #the right angle from each record
    left_angles = [sublist[1] for sublist in last_two_values] #the left angle from each record


    #extract the joints names and create graphs names
    first_values= list_joints[0]
    first_6_values= first_values[:6]
    joints_names = [str(sample).split()[0] for sample in first_6_values]
    first_graph_name= joints_names[0]+", "+joints_names[1]+", "+joints_names[2]
    second_graph_name= joints_names[3]+", "+joints_names[4]+", "+joints_names[5]

    #create a list of x values
    length= len(list_joints)
    measurement_num = list(range(1, length + 1))

    #create a data dic for graph
    data = {
    first_graph_name: {'x': measurement_num, 'y': right_angles},
    second_graph_name: {'x': measurement_num, 'y': left_angles}}

    create_and_save_graph(data, exercise_name)


def two_angles_graph(exercise_name, list_joints):
    last_four_values = [entry[-4:] for entry in list_joints]  # extract from each record the last 4 values (the angles)
    right_angles = [sublist[0] for sublist in last_four_values]  # the right angle from each record
    left_angles = [sublist[1] for sublist in last_four_values]  # the left angle from each record
    right_angles2 = [sublist[2] for sublist in last_four_values]  # the second right angle from each record
    left_angles2 = [sublist[3] for sublist in last_four_values]  # the second left angle from each record

    # extract the joints names and create graphs names
    first_values = list_joints[0]
    first_12_values = first_values[:12]
    joints_names = [str(sample).split()[0] for sample in first_12_values]
    first_graph_name = joints_names[0] + ", " + joints_names[1] + ", " + joints_names[2]
    second_graph_name = joints_names[3] + ", " + joints_names[4] + ", " + joints_names[5]
    third_graph_name = joints_names[6] + ", " + joints_names[7] + ", " + joints_names[8]
    fourth_graph_name = joints_names[9] + ", " + joints_names[10] + ", " + joints_names[11]

    # create a list of x values
    length = len(list_joints)
    measurement_num = list(range(1, length + 1))

    # create a data dic for graph
    data = {
        first_graph_name: {'x': measurement_num, 'y': right_angles},
        second_graph_name: {'x': measurement_num, 'y': left_angles},
        third_graph_name: {'x': measurement_num, 'y': right_angles2},
        fourth_graph_name: {'x': measurement_num, 'y': left_angles2}
    }

    create_and_save_graph(data, exercise_name)


def three_angles_graph(exercise_name, list_joints):
    last_four_values = [entry[-6:] for entry in list_joints]  # extract from each record the last 6 values (the angles)
    right_angles = [sublist[0] for sublist in last_four_values]  # the right angle from each record
    left_angles = [sublist[1] for sublist in last_four_values]  # the left angle from each record
    right_angles2 = [sublist[2] for sublist in last_four_values]  # the second right angle from each record
    left_angles2 = [sublist[3] for sublist in last_four_values]  # the second left angle from each record
    right_angles3 = [sublist[4] for sublist in last_four_values]  # the third right angle from each record
    left_angles3 = [sublist[5] for sublist in last_four_values]  # the third left angle from each record

    # extract the joints names and create graphs names
    first_values = list_joints[0]
    first_18_values = first_values[:18]
    joints_names = [str(sample).split()[0] for sample in first_18_values]
    first_graph_name = joints_names[0] + ", " + joints_names[1] + ", " + joints_names[2]
    second_graph_name = joints_names[3] + ", " + joints_names[4] + ", " + joints_names[5]
    third_graph_name = joints_names[6] + ", " + joints_names[7] + ", " + joints_names[8]
    fourth_graph_name = joints_names[9] + ", " + joints_names[10] + ", " + joints_names[11]
    fifth_graph_name = joints_names[12] + ", " + joints_names[13] + ", " + joints_names[14]
    sixth_graph_name = joints_names[15] + ", " + joints_names[16] + ", " + joints_names[17]

    # create a list of x values
    length = len(list_joints)
    measurement_num = list(range(1, length + 1))

    # create a data dic for graph
    data = {
        first_graph_name: {'x': measurement_num, 'y': right_angles},
        second_graph_name: {'x': measurement_num, 'y': left_angles},
        third_graph_name: {'x': measurement_num, 'y': right_angles2},
        fourth_graph_name: {'x': measurement_num, 'y': left_angles2},
        fifth_graph_name: {'x': measurement_num, 'y': right_angles3},
        sixth_graph_name: {'x': measurement_num, 'y': left_angles3}
    }

    create_and_save_graph(data, exercise_name)



def create_and_save_graph(data, exercise):
    # Define the starting row and column for inserting the graphs
    # Iterate over each plot data
    for plot_name, plot_data in data.items():
        # Create a new plot
        plt.plot(plot_data['x'], plot_data['y'])
        plt.xlabel('מספר מדידה'[::-1])
        plt.ylabel('זווית'[::-1])
        plt.title(plot_name)

        # Add text box with statistics
        min_val = f"{min(plot_data['y']):.2f}"
        max_val = f"{max(plot_data['y']):.2f}"
        average = f"{(sum(plot_data['y']) / len(plot_data['y'])):.2f}"
        stdev = f"{np.std(plot_data['y']):.2f}"

        text = f" {min_val} :מינימום \n {max_val} :מקסימום \n  {average} :ממוצע \n {stdev} :סטיית תקן"
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]+')
        text_content= hebrew_pattern.sub(lambda match: match.group(0)[::-1], text)

        plt.text(1, 1, text_content, transform=plt.gca().transAxes, verticalalignment='top',
                 horizontalalignment='right', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Save the plot as an image file
        date_and_time_of_training= s.training_workbook_name.replace(".xlsx", "") #only the date and time of a training
        create_and_open_folder(f'Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{date_and_time_of_training}')
        plot_filename = f'Patients/{s.chosen_patient_ID}/Graphs/{exercise}/{date_and_time_of_training}/{plot_name}.jpeg'
        plt.savefig(plot_filename)
        plt.close()  # Close the plot to clear the figure


        #s..insert_image(f"A{start_row}", plot_filename)
    #s.training_workbook.save()


def success_worksheet():
    s.success_sheet = s.training_workbook.add_worksheet("success")
    s.success_sheet.write(0, 0, "exercise")
    s.success_sheet.write(0, 1, "number of successful repetitions")

    row = 1
    for exercise, success in s.ex_list.items():
        s.success_sheet.write(row, 0, exercise)
        s.success_sheet.write(row, 1, success)

        row += 1


def effort_worksheet():
    s.effort_sheet = s.training_workbook.add_worksheet("effort")
    s.effort_sheet.write(0, 0, "exercise")
    s.effort_sheet.write(0, 1, "effort")

    row = 1
    for exercise, effort in s.list_effort_each_exercise.items():
        s.effort_sheet.write(row, 0, exercise)
        s.effort_sheet.write(row, 1, effort)

        row += 1


def find_and_change_values_exercises(new_values_dict, headers_row=1):
    # Load the workbook
    file_path = "Patients.xlsx"
    workbook = openpyxl.load_workbook(file_path)

    # Select the desired sheet
    sheet = workbook["patients_exercises"]

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


def find_and_change_values_patients(new_values_dict, headers_row=1):
    # Load the workbook
    file_path = "Patients.xlsx"
    workbook = openpyxl.load_workbook(file_path)

    # Select the desired sheet
    sheet = workbook["patients_details"]

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
            # Initialize next_column to 1
            next_column = 1

            # Find the next available column in the found row
            for col in range(1, sheet.max_column + 1):
                if sheet.cell(row=cell.row, column=col).value is not None:
                    next_column = col + 1

            # Write the new value to the next available column in the found row
            sheet.cell(row=cell.row, column=next_column, value=s.training_workbook_name.replace(".xlsx", ""))  # training name
            sheet.cell(row=cell.row, column=next_column + 1, value=(s.number_of_repetitions_in_training / s.max_repetitions_in_training))  # percent of the training that the patient managed to do

            break  # Stop searching after finding the value

    workbook.save(file_path)


# counts number of exercises in a training by ID by counting the true value
def count_number_of_exercises_in_training_by_ID():
    # Select the specific sheet
    workbook = openpyxl.load_workbook("Patients.xlsx")

    sheet = workbook["patients_exercises"]

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
    s.training_workbook.close()






if __name__ == "__main__":


    find_value_by_colName_and_userID("314808981", "email")

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