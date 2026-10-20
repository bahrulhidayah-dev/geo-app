# Sharing GeoChem App: portable and online versions

There are three ways to let other people use GeoChem App.

| Way | For whom | Needs |
|---|---|---|
| Portable Windows folder | Friends with a Windows PC, also offline (field work, lab PCs) | A ZIP file (~150 MB); no installation, no internet |
| Online (Streamlit Community Cloud) | Anyone with a browser, any system, also phones and tablets | Only the link; the developer needs free GitHub and Streamlit accounts |
| From the source code | Developers and users of macOS or Linux | Python 3.12 or newer |

## 1. Portable Windows version

### Build the ZIP file (developer, once per release)

1. Make sure the app works on your computer (`.venv` with the libraries).
2. Open the folder `geo-app\tools\portable` and double-click
   **build_portable.bat**.
3. The script downloads the official embeddable Python 3.12 from python.org
   and the libraries from pypi.org, copies the app and the examples, tests
   the result and makes
   `geo-app\dist\GeoChemApp-<version>-windows-portable.zip`.
   It needs internet and takes about 5-10 minutes.
4. Share the ZIP file (USB drive, Google Drive, e-mail link ...).

### Use it (friend)

1. Extract the whole ZIP file (right-click > *Extract All*).
2. Double-click **Start GeoChem App.bat**.
3. The browser opens the app after 10-30 seconds. Keep the black window
   open; close it to stop the app.

If Windows shows *Windows protected your PC*, click *More info* > *Run
anyway* (the warning appears for every file that came from the internet).

The portable folder contains:

```
GeoChemApp-<version>-windows-portable\
  Start GeoChem App.bat     double-click to start
  READ ME FIRST.txt
  launcher.py               finds a free port and opens the browser
  python\                   embeddable Python 3.12 with the libraries
  app\                      the app (app.py, geochem\, docs\, LICENSE ...)
  examples\                 example data files
```

## 2. Online version (Streamlit Community Cloud)

Streamlit Community Cloud runs the app for free from a GitHub repository
and gives it a public address. The official instance is https://geo-app-hidayah.streamlit.app
(repository: https://github.com/bahrulhidayah-dev/geo-app).

### Step 1 - Put the code on GitHub

1. Create a free account at github.com.
2. Upload the code, in one of these ways:
   - **GitHub Desktop** (easiest for beginners; this is how the official
     repository was made):
     1. *Add an Existing Repository from your local drive* > choose the
        `geo-app` folder.
     2. GitHub Desktop says the folder is not a Git repository yet: click
        **create a repository**. Keep the name `geo-app`, leave *README*,
        *Git ignore* and *License* empty (the files already exist), and click
        **Create repository**. GitHub Desktop makes the first commit
        (*Initial commit*) by itself, so the *Changes* tab shows
        *0 changed files*; the committed files are listed in the *History*
        tab.
     3. Click **Publish repository**, untick **Keep this code private**,
        and click **Publish repository** again.
   - **Command line** (in the `geo-app` folder; first create an empty
     public repository named `geo-app` on github.com):

     ```
     git init
     git add .
     git commit -m "GeoChem App"
     git branch -M main
     git remote add origin https://github.com/<your-name>/geo-app.git
     git push -u origin main
     ```

   The file `.gitignore` keeps `.venv`, `dist`, `test_data` and
   `reference` out of the repository, so your own data are not published.
   Check the file list on GitHub before you continue.

### Step 2 - Deploy

1. Go to share.streamlit.io and sign in with GitHub.
2. Click **Create app** > **Deploy a public app from GitHub**.
3. Choose the repository `<your-name>/geo-app`, branch `main`, main file
   `app.py`.
4. Optional: choose a custom address (the official one is
   `geo-app-hidayah`).
5. Under **Advanced settings**, choose Python **3.12**.
6. Click **Deploy**. The first start takes a few minutes; later starts are
   fast.

### Step 3 - Updates

Every change pushed to GitHub updates the online app automatically within
a minute. In GitHub Desktop:

1. The *Changes* tab lists the changed files. Write a short summary (for
   example `Fix top bar`) and click **Commit to main**.
2. Click **Push origin**.

If the button shows **Pull origin** instead (with arrows ↓1 ↑1), GitHub has
a commit that your computer does not have yet. Click **Pull origin** first;
GitHub Desktop merges both, and then **Push origin** appears.

This happens, for example, after you click the pencil icon (✏️) on the
online app: Streamlit then adds a `.devcontainer` folder to the repository
(settings for editing the code in the browser with GitHub Codespaces). The
folder is harmless and can stay.

### Good to know

- **Privacy:** on the online version, uploaded files are processed in the
  server's memory and are not saved, but they do leave the user's computer.
  The app shows this note in the left panel. Confidential data should be
  analysed with the portable or desktop version.
- **Sleeping:** a free app that nobody opened for some days goes to sleep;
  the next visitor clicks *Yes, get this app back up* and waits about a
  minute.
- **Resources:** the free plan has about 1 GB of memory, enough for data
  tables of thousands of samples.
- **Theme:** each visitor's light/dark choice is stored in his or her own
  browser.

### Maintenance mode (closing the app for a while)

During a critical update you can close the online app without changing the
code:

1. Open the settings: either on share.streamlit.io > *My apps* > **⋮**
   next to the app > **Settings** > **Secrets**, or in the online app
   itself > **Manage app** (bottom right, visible only to you) > **⋮** >
   **Settings** > **Secrets**. (The **Share** button at the top right is a
   different panel: it invites viewers and switches the app between public
   and private; keep *Make this app public* on.)
2. Add these lines and click **Save**:

   ```
   MAINTENANCE = true
   MAINTENANCE_MESSAGE = "The app is serpentinising. New features coming soon!"
   MAINTENANCE_KEY = "choose-a-secret-word"
   ```

   Only `MAINTENANCE` is required; choose your own secret word (anyone who
   knows it can open the app). Within about a minute visitors see a short
   notice in English, Indonesian and Japanese, with your message and contact
   e-mail. The code for this switch must already be on GitHub (version
   0.9.1 or later).
3. You can still use the app yourself at
   `https://geo-app-hidayah.streamlit.app/?key=choose-a-secret-word`.
   A yellow bar reminds you that maintenance mode is on.
4. To open the app again, delete the lines (or write `MAINTENANCE = false`)
   and click **Save**.

The link stays the same. For everyday fixes, work in a separate branch
(for example `dev`) and merge into `main` when the change is tested: the
online app follows `main` only.

On your own computer and in the portable version the switch is never on
(there is no Secrets file). On other servers, use the environment variables `GEOCHEM_MAINTENANCE=1`,
`GEOCHEM_MAINTENANCE_MESSAGE` and `GEOCHEM_MAINTENANCE_KEY`.

### Other hosts

The app is a standard Streamlit app and also runs on Hugging Face Spaces
(choose the *Streamlit* SDK), on a university server or in Docker:

```
pip install -r requirements.txt
streamlit run app.py --server.port 80 --server.headless true
```

On your own server, set the environment variable `GEOCHEM_HOSTED=1` so that
the app shows the privacy note.

## 3. From the source code (any system)

```
git clone https://github.com/bahrulhidayah-dev/geo-app.git
cd geo-app
python -m venv .venv
.venv\Scripts\activate              (Windows)
source .venv/bin/activate           (macOS, Linux)
pip install -r requirements.txt
streamlit run app.py
```

## Release checklist (developer)

1. Raise `APP_VERSION` in `app.py` and `version` in `CITATION.cff`.
2. Add the changes to `CHANGELOG.md`.
3. Test with the files in `examples/`.
4. Commit and push to GitHub (the online version updates itself). Use
   maintenance mode if the update may break the app for a while.
5. Run `tools\portable\build_portable.bat` and share the new ZIP file.
6. Optional: make a GitHub *Release* and connect the repository to
   zenodo.org to get a DOI that others can cite.
