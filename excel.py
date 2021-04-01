import pandas as pd

FILE_TITLE = "CommitHistory"


def create_table_for_author(file_name, content, column_widths=None):
    if not content:
        return

    df = pd.DataFrame(content)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    fname = "%s.xlsx" % file_name
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')

    # Write the dataframe data to XlsxWriter. Turn off the default header and
    # index and skip one row to allow us to insert a user defined header.
    df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Create a list of column headers, to use in add_table().
    column_settings = [{'header': column} for column in df.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    if column_widths:
        for i, width in enumerate(column_widths):
            worksheet.set_column(i, i, width)

    writer.save()

def read_excel_file(fname):
    import pandas as pd
    xl = pd.ExcelFile(fname)
    xl.sheet_names

    df = xl.parse("Sheet1")
    return df

if __name__ == "__main__":
    fname = "/home/czs/author_msgs/'zhenshan.cao'.xlsx"
    df = read_excel_file(fname)
    print(df)