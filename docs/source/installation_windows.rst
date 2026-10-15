Windows: installation and first launch
======================================

This guide uses **Windows PowerShell** on a Windows 10/11 x64 PC and Python
3.14 (64-bit). KinOpt opens a graphical interface; you do not need an editor
or programming experience to use it. An Internet connection is needed during
installation to download Python packages.

1. Install Python
-----------------

Install the **Python Install Manager** from the
`official Python website <https://www.python.org/downloads/windows/>`_.
After installation, open a new PowerShell window from the Start menu and run:

.. code-block:: powershell

    pymanager install 3.14
    py -3.14 --version

The second command should print ``Python 3.14.x``. If that version is already
installed, you can skip the first command. This guide selects Python 3.14
explicitly because it is one of the versions tested for KinOpt.

See the `Python Windows installation guide <https://docs.python.org/3.14/using/windows.html>`_
if the manager or ``py`` command is not found.

2. Download and extract KinOpt
------------------------------

1. Open the `KinOpt repository <https://github.com/alan-tabore/KinOpt>`_.
2. Choose **Code → Download ZIP**. When trying a pull request, select that
   pull request's branch before downloading.
3. Right-click the downloaded ZIP and choose **Extract All**.
4. Put the extracted project in a permanent folder, for example
   ``C:\Users\Alice\KinOpt``. Replace ``Alice`` with your Windows account name.
   The folder should directly contain ``pyproject.toml``, ``README.md`` and
   the ``kinopt`` subfolder. Do not run the application from inside the ZIP.

The commands below assume this folder is named ``KinOpt`` inside your user
profile. If you choose another location, replace the paths accordingly.

3. Install KinOpt in its own environment
-----------------------------------------

In PowerShell, run each line separately:

.. code-block:: powershell

    Set-Location "$env:USERPROFILE\KinOpt"
    py -3.14 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install .
    .\.venv\Scripts\python.exe -m pip check

The dot at the end of ``pip install .`` means "install the project in this
folder". Wait for installation to finish before entering the next command.
``pip check`` should report ``No broken requirements found.``

The ``.venv`` folder holds Python and the packages used by KinOpt. These
commands invoke its executables directly: you do not need to activate it
or change PowerShell's script execution policy. This follows Python's
`virtual environment usage <https://docs.python.org/3.14/library/venv.html#how-venvs-work>`_.

4. Open the application
-----------------------

From the same project folder:

.. code-block:: powershell

    .\.venv\Scripts\kinopt.exe

The KinOpt window should open. The PowerShell prompt returns when you close
the application. Leave the terminal open while using KinOpt.

On later days, you only need to open PowerShell and run these two lines:

.. code-block:: powershell

    Set-Location "$env:USERPROFILE\KinOpt"
    .\.venv\Scripts\kinopt.exe

You can also launch it from any folder with its full path:

.. code-block:: powershell

    & "$env:USERPROFILE\KinOpt\.venv\Scripts\kinopt.exe"

The leading ``&`` tells PowerShell to execute a quoted path. It also handles
folder names containing spaces; see Microsoft's
`PowerShell call operator documentation <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_operators#call-operator->`_.

An equivalent launch through Python is:

.. code-block:: powershell

    .\.venv\Scripts\python.exe -m kinopt

5. Create a desktop shortcut (optional)
---------------------------------------

1. In File Explorer, open your project folder, then ``.venv\Scripts``.
2. Right-click ``kinopt.exe``. On Windows 11, select **Show more options** if
   necessary, then **Send to → Desktop (create shortcut)**.
3. Rename the shortcut **KinOpt**. Double-click it to open the application.

This launcher also opens a console window. Keep it open with KinOpt. If the
application closes unexpectedly, use the PowerShell launch above to read
the error message. Keep the project in the same location after installation;
recreate the environment and shortcut if you move it.

If you prefer to type only ``kinopt`` in any new terminal, add the full path
of ``KinOpt\.venv\Scripts`` to your **user Path** through **Edit environment
variables for your account → Path → Edit → New**, then open a new terminal.
The full-path command and desktop shortcut do not require this optional step.

6. Try the included data
------------------------

In the **Data extraction** panel:

1. Click **Try Kamal example**, then **OK** after extraction. The four included
   files are loaded and the file list becomes green.
2. Use **Rate**, **Extent** and **Temperature** to inspect the imported curves.

For a short optimization trial:

1. Check the prepared ``rate_for_kamal`` model and its illustrative starting
   values. Vitrification, coupling and Tg remain unselected.
2. Check the prepared local method ``Nelder-Mead``, cost function ``rss_mean``,
   and **Quick check** calculation profile.
3. Click **Review setup…**, then start the optimization. Inspect the curves and solver message when it
   finishes. You can also test **Cancel optimization**, then start another run.

This short trial checks the application workflow. Reaching the iteration limit
does not mean the model is fully fitted; a successful installation alone does
not validate a scientific result.

7. Find or choose the result folder
-----------------------------------

By default, new results are saved in ``KinOpt\results`` inside the **Documents**
folder configured in Windows. The exact path appears after **Results saved to:**
in the optimization output panel. Use that path if Windows redirects Documents
to another location, such as OneDrive.

To choose a different folder when launching:

.. code-block:: powershell

    .\.venv\Scripts\kinopt.exe --results-dir "$env:USERPROFILE\KinOpt Results"

Keep the quotes around a path containing spaces. KinOpt creates the directory
when saving a result. To reopen a saved result, use **Load result file(s)**,
select the file in the list, then click **Display selected result file**.

8. Update an existing installation
-----------------------------------

Close KinOpt, update the project files in the same folder (using Git or an
extracted ZIP), then run:

.. code-block:: powershell

    Set-Location "$env:USERPROFILE\KinOpt"
    .\.venv\Scripts\python.exe -m pip install .
    .\.venv\Scripts\python.exe -m pip check

You can then launch it as before. Files saved in Documents or a custom results
folder are separate from the installation.

Troubleshooting
---------------

``pymanager`` or ``py`` is not recognized
    Close and reopen PowerShell after installing the Python Install Manager.
    Follow the official Python Windows guide linked above if the command is
    still missing. With an older Python launcher, ``py -3.14 --version`` may
    already work even when ``pymanager`` is not installed.

``pip install .`` says the directory is not installable
    Check that PowerShell is in the extracted folder containing
    ``pyproject.toml``. ZIP extraction may create an extra outer folder.

``kinopt`` is not recognized
    Use ``.\.venv\Scripts\kinopt.exe`` from the project folder, or the full-path
    command above. A bare ``kinopt`` command needs the Scripts folder on Path.

PowerShell reports that running scripts is disabled
    Use the ``.exe`` commands in this guide. They do not require running
    ``Activate.ps1`` or changing the execution policy.

The window immediately closes, or ``No module named kinopt`` appears
    Launch from PowerShell to keep the error visible. Make sure you use
    ``.\.venv\Scripts\python.exe`` for installation and launch. Check with:

    .. code-block:: powershell

        .\.venv\Scripts\python.exe -m pip check
        .\.venv\Scripts\kinopt.exe --version

    Copy the full error message if you need help. If package installation
    failed, resolve that error before retrying the launch.

Results cannot be written
    Launch with ``--results-dir`` pointing to a folder you can write to, as in
    step 7. The application displays an error if saving fails.
