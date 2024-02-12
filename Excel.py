import os
import xlsxwriter
import openpyxl
from datetime import datetime
import Settings as s
from Joint import Joint


def create_workbook():
    datetime_string = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    workbook_name = f"{s.chosen_patient_ID}- {datetime_string}.xlsx"
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


def success_worksheet():
    s.success_sheet = s.excel_workbook.add_worksheet("success")
    s.success_sheet.write(0, 0, "exercise")
    s.success_sheet.write(0, 1, "number of successful repetitions")

    row = 1
    for exercise, effort in s.ex_list.items():
        s.success_sheet.write(row, 0, exercise)
        s.success_sheet.write(row, 1, effort)

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

def find_and_change_values_Patients(search_value, new_values_dict, headers_row=1):
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
        if str(cell.value) == search_value:
            # Update the values in the corresponding columns
            for header_name, column_index in column_indices.items():
                sheet.cell(row=cell.row, column=column_index, value=new_values_dict[header_name])

    # Save the changes
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
