from kivy.app import App
from kivy.uix.label import Label
import os
from datetime import datetime
import pytz

class MyApp(App):
    def build(self):
        # Convert current time to IST
        ist = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(ist)


        if current_time.day == 10 and current_time.hour >= 7:  # First day of month & at or after 7 AM
            file_path = "attendance_data.json"  # Update with actual file path
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} deleted at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
            else:
                print("File not found!")

        return Label(text="Welcome to My Kivy App")

if __name__ == "__main__":
    MyApp().run()
