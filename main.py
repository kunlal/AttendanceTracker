import json
import os

import pytz
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from datetime import datetime, timedelta
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle  # For color changes
from kivy.uix.progressbar import ProgressBar
from plyer import notification
import time
import threading
import calendar

class AttendanceCalendar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.current_month = datetime.now().month
        print("Current Month",self.current_month)
        self.current_year = datetime.now().year
        self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        self.holidays = set()
        self.attendance = self.load_data()
        self.create_calendar()



    def load_data(self):
        try:
            with open("attendance_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_data(self):
        with open("attendance_data.json", "w") as file:
            json.dump(self.attendance, file)



    def create_calendar(self):
        self.clear_widgets()

        img = Image(source='attendance.jpg', size_hint=(1, 0.6))
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

            # Apply blue color if the date is marked as Holiday in JSON
            if status == "Holiday":
                button_color = (0, 0, 1, 1)  # Blue
            elif status == "WFO":
                button_color = (0, 1, 0, 1)  # Green
            elif status == "WFH":
                button_color = (1, 0, 0, 1)  # Red
            else:
                button_color = (1, 1, 1, 1)  # Default White

            button = Button(
                text=date_str,
                background_color=button_color,
                disabled=datetime(self.current_year, self.current_month, day).weekday() in [5, 6]
            )

            button.bind(on_release=lambda btn: self.mark_attendance(btn))
            grid.add_widget(button)

        bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=100)

        # Button Section
        # Button Section
        button_layout = BoxLayout(orientation='vertical', size_hint=(0.4, None))
        button_layout.add_widget(Button(text="Add Leave", on_release=self.add_holiday))
        button_layout.add_widget(Button(text="Reset A Date", on_release=self.reset_date))
        button_layout.add_widget(Button(text="Show", on_release=self.calculate_attendance))

        # Summary Section

        self.attendance_summary = BoxLayout(orientation='vertical', size_hint=(0.6, None))

        self.getData = self.get_attendance_summary()
        percentage = self.getData.split("\n")[3].split(":")[1].rstrip("%")

        color = (1, 0, 0, 1) if float(percentage) < 60 else (0, 1, 0, 1)


        self.summary_label = Label(text=self.get_attendance_summary() ,color=color,size_hint=(1, None))



        self.attendance_summary.add_widget(self.summary_label)


        # Add both sections to the bottom layout
        self.add_widget(grid)
        bottom_layout.add_widget(button_layout)
        bottom_layout.add_widget(self.attendance_summary)

        # Add the entire bottom layout to the main widget
        self.add_widget(bottom_layout)

    def get_attendance_summary(self):
        total_days = len([day for day in range(1, self.days_in_month+1) if
                          datetime(self.current_year, self.current_month, day).weekday() not in [5,
                                                                                                 6]])

        leave_days = sum(1 for day in self.attendance.values() if day == "Holiday")

        WFO_days = sum(1 for day in self.attendance.values() if day == "WFO")
        WFH_days = sum(1 for day in self.attendance.values() if day == "WFH")

        total_working_days = total_days-leave_days

        percentage = (WFO_days / (total_days-leave_days)) * 100 if total_days else 0


        return f"Working Days: {total_working_days}\nWFO (Office): {WFO_days}\nWFH (Home): {WFH_days}\nWFO (%): {percentage:.2f}%"

    def update_attendance_summary(self):
        self.summary_label.text = self.get_attendance_summary()

    def mark_attendance(self, instance):
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

    def update_attendance(self, day, status, popup):
        self.attendance[str(day)] = status

        # If a holiday exists on this day, remove it
        if int(day) in self.holidays:
            self.holidays.remove(int(day))

        # Save changes, update attendance summary, and refresh the calendar
        self.save_data()
        self.update_attendance_summary()
        self.create_calendar()
        popup.dismiss()

    def reset_date_manually(self, day):
        """ Resets a date before adding a holiday. """
        if str(day) in self.attendance:
            del self.attendance[str(day)]

        if day in self.holidays:
            self.holidays.remove(day)

        # Save and refresh
        self.save_data()
        self.update_attendance_summary()
        self.create_calendar()
    def add_holiday(self, instance):
        popup = Popup(title="Enter Holiday Date", size_hint=(0.6, 0.4))
        box = BoxLayout(orientation='vertical')
        input_field = TextInput(hint_text="Enter holiday day (number)")
        submit_btn = Button(text="Add")

        def save_holiday(btn):
            try:
                holiday = int(input_field.text)

                # Call reset_date before adding a holiday
                self.reset_date_manually(holiday)

                # Add holiday to attendance record
                self.attendance[str(holiday)] = "Holiday"

                # Save changes to JSON
                self.save_data()

                # Refresh total working days and attendance summary
                self.update_attendance_summary()

                # Update UI
                self.holidays.add(holiday)
                self.create_calendar()
                popup.dismiss()

            except ValueError:
                input_field.text = "Invalid number!"

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

                # Remove from holidays if it exists
                if day in self.holidays:
                    self.holidays.remove(day)

                # Remove attendance record if it exists
                if str(day) in self.attendance:
                    del self.attendance[str(day)]

                # Save changes and refresh the calendar
                self.save_data()
                self.create_calendar()
                popup.dismiss()

            except ValueError:
                input_field.text = "Invalid number!"

        submit_btn.bind(on_release=reset_specific_day)
        box.add_widget(input_field)
        box.add_widget(submit_btn)
        box.add_widget(Button(text="Close", on_release=popup.dismiss))
        popup.add_widget(box)
        popup.open()

    def calculate_attendance(self, instance):
        total_days = len([day for day in range(1, self.days_in_month+1) if
                          datetime(self.current_year, self.current_month, day).weekday() not in [5,
                                                                                                 6] and day not in self.holidays])
        leave_days = sum(1 for day in self.attendance.values() if day == "Holiday")
        WFO_days = sum(1 for day in self.attendance.values() if day == "WFO")
        percentage = (WFO_days / (total_days-leave_days)) * 100 if total_days else 0
        color = (1, 0, 0, 1) if percentage < 60 else (0, 1, 0, 1)
        total_working_days = total_days - leave_days
        popup = Popup(title="Attendance Summary", size_hint=(0.6, 0.4))
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=f"Week Days: {total_days}"))
        box.add_widget(Label(text=f"Working Days: {total_working_days}"))
        box.add_widget(Label(text=f"WFO Days: {WFO_days}"))
        box.add_widget(Label(text=f"WFO Percentage: {percentage:.2f}%",color=color))
        summary = Button(text="Close", background_color=color)
        summary.bind(on_release=popup.dismiss)
        box.add_widget(summary)
        popup.add_widget(box)
        popup.open()


class AttendanceApp(App):
    def build(self):
        # Schedule notification every morning
        ist = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(ist)

        if current_time.day == 1 and current_time.hour >= 7:  # First day of month & at or after 7 AM
            file_path = "attendance_data.json"  # Update with actual file path
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} deleted at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
            else:
                print("File not found!")
        threading.Thread(target=self.schedule_notification, daemon=True).start()
        # return AttendanceCalendar()
        return AttendanceCalendar()

    def schedule_notification(self):
        while True:
            current_hour = datetime.now().hour
            if current_hour == 8:  # 8 AM Morning Reminder
                notification.notify(
                    title="Attendance Reminder",
                    message="Update your attendance for today!",
                    timeout=10
                )
                time.sleep(86400)  # Wait 24 hours for next notification
            else:
                time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    AttendanceApp().run()
