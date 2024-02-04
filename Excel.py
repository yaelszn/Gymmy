import os
import xlsxwriter
import datetime
import Settings as s
import openpyxl
from datetime import datetime


def create_workbook():
    datetime_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    workbook_name = f"{s.chosen_patient_ID}- {datetime_string}.xlsx"
    s.excel_workbook = xlsxwriter.Workbook(workbook_name)
    s.success_sheet = s.excel_workbook.add_worksheet("success")
    s.success_sheet.write(0, 0, "exercise")
    s.success_sheet.write(0, 1, "number of successful repetitions")

    create_Last_workbook()


def create_Last_workbook():
    file_path = f"{s.chosen_patient_ID}_Last.xlsx"

    try:
        # Load the existing workbook into a variable
        s.Last_workbook = openpyxl.load_workbook(file_path)
    except FileNotFoundError:
        print(f"File '{file_path}' not found. Creating a new workbook.")
        s.Last_workbook = xlsxwriter.Workbook(file_path)
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def wf_joints(ex_name, list_joints, successful_repetitions):
    if ex_name in s.Last_workbook.sheetnames:
        # Remove the existing sheet
        s.Last_workbook.remove(s.Last_workbook[ex_name])

    worksheet1 = s.excel_workbook.add_worksheet(ex_name)
    worksheet2 = s.Last_workbook.create_sheet(title=ex_name)
    col = 0

    for l in range(1, len(list_joints)):
        row = 1
        worksheet1.write(0, col, col + 1)
        worksheet2.write(0, col, col + 1)

        for j in list_joints[l]:
            j_ar = j.joint_to_array()
            for i in range(len(j_ar)):
                worksheet1.write(row, col, str(j_ar[i]))
                worksheet2.write(row, col, str(j_ar[i]))

                row += 1

        col += 1

    success_worksheet(ex_name,successful_repetitions)

def success_worksheet(ex_name, successful_repetitions):
    existing_rows = s.success_sheet.dim_rowmax

    # Add the new data to the next available row
    s.success_sheet.write(existing_rows, 0, ex_name)
    s.success_sheet.write(existing_rows, 1, successful_repetitions)

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





def close_workbook():
    s.Last_workbook.close()
    s.excel_workbook.close()

