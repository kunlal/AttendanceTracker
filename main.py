import os

# Your updated main.py with logging and exception handling added
import os
import json
import pytz
import time
import threading
import calendar
import logging
from datetime import datetime, timedelta

# Setup logging
kivy_home = os.path.join(os.getcwd(), 'kivy_home')
os.environ['KIVY_HOME'] = kivy_home
if not os.path.exists(kivy_home):
    os.makedirs(kivy_home)

log_file = os.path.join(kivy_home, 'app.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logging.info("Application started.")

# Disable icon copying to avoid Android permission error
os.environ["KIVY_NO_FILELOG"] = "1"
import kivy.resources
kivy.resources.install_kivy_icon = lambda: None

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.utils import platform
from kivy.resources import resource_find
from plyer import notification

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


class AttendanceCalendar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        try:
            self.current_month = datetime.now().month
            self.current_year = datetime.now().year
            self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
            self.holidays = set()
            self.attendance = self.load_data()
            self.create_calendar()
        except Exception as e:
            logging.error(f"Initialization error: {e}")

    def load_data(self):
        try:
            with open("attendance_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning("Attendance data file not found. Creating new data.")
            return {}
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            return {}

    def save_data(self):
        try:
            with open("attendance_data.json", "w") as file:
                json.dump(self.attendance, file)
            logging.info("Attendance data saved.")
        except Exception as e:
            logging.error(f"Failed to save data: {e}")

    def create_calendar(self):
        try:
            self.clear_widgets()
            image_path = resource_find('attendance.jpg')
            if image_path:
                img = Image(source=image_path, size_hint=(1, 0.6))
            else:
                img = Label(text="[Image not found]", size_hint=(1, 0.6))
            self.add_widget(img)

            self.add_widget(Label(text=f"{datetime(self.current_year, self.current_month, 1):%B %Y}", size_hint=(1, 0.3)))
            grid = GridLayout(cols=7)
            weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for day in weekdays:
                grid.add_widget(Label(text=day))

            first_day_of_month = datetime(self.current_year, self.current_month, 1).weekday()
            days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]

            for _ in range(first_day_of_month):
                grid.add_widget(Label(text=""))

            for day in range(1, days_in_month + 1):
                date_str = str(day)
                status = self.attendance.get(date_str, "None")
                button_color = {
                    "Holiday": (0, 0, 1, 1),
                    "WFO": (0, 1, 0, 1),
                    "WFH": (1, 0, 0, 1)
                }.get(status, (1, 1, 1, 1))
                button = Button(
                    text=date_str,
                    background_color=button_color,
                    disabled=datetime(self.current_year, self.current_month, day).weekday() in [5, 6]
                )
                button.bind(on_release=lambda btn: self.mark_attendance(btn))
                grid.add_widget(button)

            bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=100)
            button_layout = BoxLayout(orientation='vertical', size_hint=(0.4, None))
            button_layout.add_widget(Button(text="Add Leave", on_release=self.add_holiday))
            button_layout.add_widget(Button(text="Reset A Date", on_release=self.reset_date))
            button_layout.add_widget(Button(text="Show", on_release=self.calculate_attendance))
            self.attendance_summary = BoxLayout(orientation='vertical', size_hint=(0.6, None))
            self.getData = self.get_attendance_summary()
            percentage = self.getData.split("\\n")[3].split(":")[1].rstrip("%")
            color = (1, 0, 0, 1) if float(percentage) < 60 else (0, 1, 0, 1)
            self.summary_label = Label(text=self.get_attendance_summary(), color=color, size_hint=(1, None))
            self.attendance_summary.add_widget(self.summary_label)
            self.add_widget(grid)
            bottom_layout.add_widget(button_layout)
            bottom_layout.add_widget(self.attendance_summary)
            self.add_widget(bottom_layout)
        except Exception as e:
            logging.error(f"Error creating calendar: {e}")

    def get_attendance_summary(self):
        try:
            total_days = len([day for day in range(1, self.days_in_month+1) if
                              datetime(self.current_year, self.current_month, day).weekday() not in [5, 6]])
            leave_days = sum(1 for day in self.attendance.values() if day == "Holiday")
            WFO_days = sum(1 for day in self.attendance.values() if day == "WFO")
            WFH_days = sum(1 for day in self.attendance.values() if day == "WFH")
            total_working_days = total_days - leave_days
            percentage = (WFO_days / total_working_days) * 100 if total_working_days else 0
            return f"Working Days: {total_working_days}\\nWFO (Office): {WFO_days}\\nWFH (Home): {WFH_days}\\nWFO (%): {percentage:.2f}%"
        except Exception as e:
            logging.error(f"Failed to compute attendance summary: {e}")
            return "Summary Error"

    def update_attendance_summary(self):
        self.summary_label.text = self.get_attendance_summary()

    def mark_attendance(self, instance):
        try:
            day = instance.text
            options = ["WFO", "WFH"]
            popup = Popup(title=f"Mark attendance for {day}", size_hint=(0.6, 0.4))
            box = BoxLayout(orientation='vertical')
            for option in options:
                btn = Button(text=option)
                btn.bind(on_release=lambda btn: self.update_attendance(day, btn.text, popup))
                box.add_widget(btn)
            popup.add_widget(box)
            popup.open()
        except Exception as e:
            logging.error(f"Error marking attendance: {e}")

    def update_attendance(self, day, status, popup):
        try:
            self.attendance[str(day)] = status
            logging.info(f"Marked day {day} as {status}")
            if int(day) in self.holidays:
                self.holidays.remove(int(day))
            self.save_data()
            self.update_attendance_summary()
            self.create_calendar()
            print("Test Code")
            popup.dismiss()
        except Exception as e:
            logging.error(f"Failed to update attendance: {e}")

    def reset_date_manually(self, day):
        try:
            if str(day) in self.attendance:
                del self.attendance[str(day)]
            if day in self.holidays:
                self.holidays.remove(day)
            self.save_data()
            self.update_attendance_summary()
            self.create_calendar()
        except Exception as e:
            logging.error(f"Error resetting date manually: {e}")

    def add_holiday(self, instance):
        popup = Popup(title="Enter Holiday Date", size_hint=(0.6, 0.4))
        box = BoxLayout(orientation='vertical')
        input_field = TextInput(hint_text="Enter holiday day (number)")
        submit_btn = Button(text="Add")

        def save_holiday(btn):
            try:
                holiday = int(input_field.text)
                self.reset_date_manually(holiday)
                self.attendance[str(holiday)] = "Holiday"
                self.save_data()
                self.update_attendance_summary()
                self.holidays.add(holiday)
                self.create_calendar()
                popup.dismiss()
            except ValueError:
                input_field.text = "Invalid number!"
                logging.warning("Invalid holiday input: not a number")
            except Exception as e:
                logging.error(f"Failed to add holiday: {e}")

        submit_btn.bind(on_release=save_holiday)
        box.add_widget(input_field)
        box.add_widget(submit_btn)
        box.add_widget(Button(text="Close", on_release=popup.dismiss))
        popup.add_widget(box)
        popup.open()

    def reset_date(self, instance):
        popup = Popup(title="Enter Date to Reset", size_hint=(0.6, 0.4))
        box = BoxLayout(orientation='vertical')
        input_field = TextInput(hint_text="Enter date number")
        submit_btn = Button(text="Reset")

        def reset_specific_day(btn):
            try:
                day = int(input_field.text)
                if day in self.holidays:
                    self.holidays.remove(day)
                if str(day) in self.attendance:
                    del self.attendance[str(day)]
                self.save_data()
                self.create_calendar()
                popup.dismiss()
            except ValueError:
                input_field.text = "Invalid number!"
                logging.warning("Invalid reset input: not a number")
            except Exception as e:
                logging.error(f"Failed to reset date: {e}")

        submit_btn.bind(on_release=reset_specific_day)
        box.add_widget(input_field)
        box.add_widget(submit_btn)
        box.add_widget(Button(text="Close", on_release=popup.dismiss))
        popup.add_widget(box)
        popup.open()

    def calculate_attendance(self, instance):
        try:
            total_days = len([day for day in range(1, self.days_in_month+1) if
                              datetime(self.current_year, self.current_month, day).weekday() not in [5, 6] and day not in self.holidays])
            leave_days = sum(1 for day in self.attendance.values() if day == "Holiday")
            WFO_days = sum(1 for day in self.attendance.values() if day == "WFO")
            percentage = (WFO_days / (total_days - leave_days)) * 100 if total_days else 0
            color = (1, 0, 0, 1) if percentage < 60 else (0, 1, 0, 1)
            total_working_days = total_days - leave_days
            popup = Popup(title="Attendance Summary", size_hint=(0.6, 0.4))
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=f"Week Days: {total_days}"))
            box.add_widget(Label(text=f"Working Days: {total_working_days}"))
            box.add_widget(Label(text=f"WFO Days: {WFO_days}"))
            box.add_widget(Label(text=f"WFO Percentage: {percentage:.2f}%", color=color))
            summary = Button(text="Close", background_color=color)
            summary.bind(on_release=popup.dismiss)
            box.add_widget(summary)
            popup.add_widget(box)
            popup.open()
        except Exception as e:
            logging.error(f"Error calculating attendance summary: {e}")


class AttendanceApp(App):
    def build(self):
        try:
            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist)
            if current_time.day == 1 and current_time.hour >= 7:
                file_path = "attendance_data.json"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Deleted {file_path} at {current_time}")
                else:
                    logging.info("No attendance file to delete on the 1st")
            threading.Thread(target=self.schedule_notification, daemon=True).start()
            return AttendanceCalendar()
        except Exception as e:
            logging.critical(f"Critical failure in build(): {e}")

    def schedule_notification(self):
        while True:
            try:
                current_hour = datetime.now().hour
                if current_hour == 8:
                    notification.notify(
                        title="Attendance Reminder",
                        message="Update your attendance for today!",
                        timeout=10
                    )
                    logging.info("Attendance notification sent.")
                    time.sleep(86400)
                else:
                    time.sleep(3600)
            except Exception as e:
                logging.error(f"Error in schedule_notification loop: {e}")


if __name__ == "__main__":
    try:
        AttendanceApp().run()
    except Exception as e:
        logging.critical(f"App crashed: {e}")

