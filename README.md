# FleetDashboardAutomation

An automated solution that logs into the MTC Bus ITS fleet management portal, downloads the daily Fleet Dashboard Excel report, and optionally uploads it to Google Drive — all running on a schedule via GitHub Actions.

## What It Can Do

- **Automated Login**: Logs into [mtcbusits.in](https://mtcbusits.in/) using stored credentials and handles CAPTCHA automatically.
- **Navigate & Download**: Navigates to the AVLS section, searches for the Fleet Dashboard report, and exports it as an Excel file (`.xlsx`).
- **Daily Scheduling**: Runs automatically every day via GitHub Actions (configurable cron schedule) — no manual intervention needed.
- **Google Drive Upload**: Optionally uploads the downloaded Excel files to a specified Google Drive folder using a service account.
- **Artifact Storage**: Saves the downloaded report as a GitHub Actions workflow artifact for easy access and download.
- **Manual Trigger**: Supports on-demand execution via the GitHub Actions `workflow_dispatch` event.

## How It Works

1. A GitHub Actions workflow triggers on schedule (or manually).
2. `Automation_Github_V1.py` launches a headless Chromium browser using Playwright.
3. It logs in, waits for the AVLS section to load, and exports the Fleet Dashboard as an Excel file.
4. The file is saved to `Fleet_Dashboard_Files/` and uploaded as a workflow artifact.
5. Optionally, `upload_to_drive.py` uploads the file to Google Drive using a service account.

## Setup

### Required Secrets (GitHub Repository Secrets)

| Secret | Description |
|---|---|
| `LOGIN_PASSWORD` | Password for the MTC Bus ITS portal login |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive folder ID to upload files into |

> **Note:** The login username is currently hardcoded in `Automation_Github_V1.py`. For improved security, consider moving it to a `LOGIN_USERNAME` repository secret.

### Google Drive Upload Setup

To enable Google Drive uploads, place a service account credentials file named `credentials.json` in the project root. You can generate this from the [Google Cloud Console](https://console.cloud.google.com/) by creating a service account with Drive API access and downloading its JSON key.

### Running Locally

```bash
pip install playwright pandas openpyxl google-auth google-api-python-client
playwright install chromium
python Automation_Github_V1.py
```

## Project Structure

```
FleetDashboardAutomation/
├── Automation_Github_V1.py      # Main automation script (login + download)
├── upload_to_drive.py           # Google Drive upload script
├── Fleet_Dashboard_Files/       # Downloaded Excel reports are saved here
└── .github/workflows/           # GitHub Actions workflow definitions
```
