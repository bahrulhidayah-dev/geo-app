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
2. Click **New repository**, name it for example `geochem-app`, choose
   **Public**, leave *Add a README* unticked, and click **Create repository**.
3. Upload the code, in one of these ways:
   - **GitHub Desktop** (easiest for beginners): install it, *File > Add
     local repository* > choose the `geo-app` folder > *Publish
     repository*.
   - **Command line** (in the `geo-app` folder):

     ```
     git init
     git add .
     git commit -m "GeoChem App 0.8.0"
     git branch -M main
     git remote add origin https://github.com/<your-name>/geochem-app.git
     git push -u origin main
     ```

   The file `.gitignore` keeps `.venv`, `dist`, `test_data` and
   `reference` out of the repository, so your own data are not published.
   Check the file list on GitHub before you continue.

### Step 2 - Deploy

1. Go to share.streamlit.io and sign in with GitHub.
2. Click **Create app** > **Deploy a public app from GitHub**.
3. Choose the repository `geochem-app`, branch `main`, main file `app.py`.
4. Optional: choose a custom address (for example `geochem-app`).
5. Under **Advanced settings**, choose Python **3.12**.
6. Click **Deploy**. The first start takes a few minutes; later starts are
   fast.

### Step 3 - Updates

Every change pushed to GitHub (`git push`, or *Push origin* in GitHub
Desktop) updates the online app automatically within a minute.

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

1. On share.streamlit.io, open the app menu (**⋮**) > **Settings** >
   **Secrets**.
2. Add these lines and click **Save**:

   ```
   MAINTENANCE = true
   MAINTENANCE_MESSAGE = "Back on 25 October."
   MAINTENANCE_KEY = "choose-a-secret-word"
   ```

   Only `MAINTENANCE` is required. Visitors now see a short notice in
   English, Indonesian and Japanese, with your message and contact e-mail.
3. You can still use the app yourself at
   `https://geo-app-hidayah.streamlit.app/?key=choose-a-secret-word`.
4. To open the app again, delete the lines (or write `MAINTENANCE = false`)
   and click **Save**.

The link stays the same. For everyday fixes, work in a separate branch
(for example `dev`) and merge into `main` when the change is tested: the
online app follows `main` only.

On other servers, use the environment variables `GEOCHEM_MAINTENANCE=1`,
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
git clone https://github.com/<your-name>/geochem-app.git
cd geochem-app
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
4. Push to GitHub (the online version updates itself).
5. Run `tools\portable\build_portable.bat` and share the new ZIP file.
6. Optional: make a GitHub *Release* and connect the repository to
   zenodo.org to get a DOI that others can cite.
