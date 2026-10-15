Extracting the data
====================

You've probably put a lot of efforts in collecting kinetic data, so let's use them.

To discover the workflow first, click **Try Kamal example**. KinOpt loads and
extracts its four included synthetic heating-rate files, selects the Kamal rate
model, fills illustrative starting values, and prepares the **Quick check**
profile. It does not start an optimization. Inspect the imported curves and
review the prepared values before clicking **Review setup…** or starting the
calculation.

Ideally, you'll have collected kinetic data for multiple temperature program.
Store them in the same folder and:

1. Click on the "Add file(s)" button of the data extraction dock
2. Navigate to the folder containing your data
3. Select all your files
4. Click the "open" button. (your files should now be loaded)
5. Check the box "has header" if the first line of your file is a header. (if you have multiple lines to skip at the beginning of your file, indicate the number of lines to skip in the entry box "Number of lines to skip".
6. Indicate the delimiter of your data in the "Delimiter" entry box. If no delimiter is indicated, the default delimiter (a comma ",") will be used. The delimiter used in the example data files is a comma ",". The tab delimiter can be specified as "\t" or "tab"
7. Click the extract button.
8. Make sure that the file list becomes green (indicating the extraction was successful)
