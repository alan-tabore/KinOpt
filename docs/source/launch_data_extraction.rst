Extracting the data
====================

You've probably put a lot of efforts in collecting kinetic data, so let's use them.

To discover the workflow first, click **Try Kamal example**. KinOpt loads and
extracts its four included synthetic heating-rate files, selects the Kamal rate
model, fills illustrative starting values, and prepares the **Quick check**
profile. It does not start an optimization. Inspect the imported curves and
review the prepared values before clicking **Review setup…** or starting the
calculation.

Ideally, you will have collected kinetic data for several temperature programs.
Store them in the same folder and:

1. Click **Add file(s)** in the data-extraction dock, select every experiment,
   and click **Open**.
2. KinOpt opens the import assistant. Choose the delimiter and the number of
   lines before the header or first data row. ``tab`` and ``\t`` both select a
   tab delimiter.
3. Check **First remaining row contains column names** when applicable. Inspect
   the preview and map the time, temperature, reaction-rate, and extent columns.
   The columns may appear in any order and unrelated columns are ignored.
4. State the unit used by each mapped column. KinOpt supports seconds or
   minutes, Kelvin or degrees Celsius, rates per second or per minute, and a
   fractional or percentage extent. Values are converted internally to
   seconds, Kelvin, ``s^-1``, and a fraction from 0 to 1.
5. Click **Validate and import**. Every selected file is checked before the
   current data are replaced. The file list turns green after a successful
   import.

The validation reports the file that contains missing or nonnumeric values,
non-increasing time, decreasing or out-of-range extent, invalid temperatures,
or a rate integral inconsistent with the extent change. Click **Review data
import...** to reopen the assistant. The original delimiter, header, and skip
fields remain available for four-column files already expressed in KinOpt's
standard units.
