from playwright.sync_api import sync_playwright
from datetime import datetime
import os

# Step 0: Setup paths and file name
today_str = datetime.now().strftime("%d-%m-%Y")
new_filename = f"Fleet Dashboard {today_str}.xlsx"

# Use environment variable for destination or default path for GitHub Actions
destination_folder = os.environ.get('DOWNLOAD_PATH', './downloads')
final_path = os.path.join(destination_folder, new_filename)

# Delete file if it exists
if os.path.exists(final_path):
    os.remove(final_path)
    print(f"🗑️ Existing file deleted: {final_path}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Changed to headless for GitHub Actions
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # Step 1: Login
            print("🔐 Logging in...")
            page.goto("https://mtcbusits.in/")
            page.fill("input[name='UserName']", "gobi.ibi")
            
            # Use environment variable for password for security
            password = os.environ.get('LOGIN_PASSWORD', 'Gobi@123')
            page.fill("input[id='password']", password)
            
            captcha_text = page.inner_text("span.input-group-addon").strip()
            page.fill("input[formcontrolname='captcha']", captcha_text)
            page.click("button:has-text('Login')")
            page.wait_for_timeout(3000)
            print("✅ Login successful")

            # Step 2: Go to AVLS section
            print("📊 Navigating to AVLS section...")
            page.click("p:has-text('AVLS')")
            page.wait_for_timeout(15000)
            print("✅ AVLS section loaded")

            # Step 3: Export Excel and save
            print("📥 Downloading Excel file...")
            with page.expect_download() as download_info:
                page.get_by_role("button", name="Export Excel All Data").click()
            download = download_info.value
            
            # Create destination folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)
            download.save_as(final_path)
            print(f"✅ File downloaded: {final_path}")

        except Exception as e:
            print(f"❌ Error occurred: {str(e)}")
            raise
        finally:
            browser.close()

    print("✅ Process completed successfully!")
    return final_path

if __name__ == "__main__":
    main()