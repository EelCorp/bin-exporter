from datetime import datetime
from time import sleep
from pathlib import Path

from icalendar import Calendar
from prometheus_client import Gauge, Info, start_http_server


ICAL = Path("bins.ics")

if __name__ == "__main__":

    time_g = Gauge('bins_next_time', 'Next time the bins need to go out')
    bin_i = Info('bin_next_type', 'Type of bins that go out next')

    start_http_server(4444)

    while True:
        now = datetime.now()

        with ICAL.open() as fh:
            cal = Calendar.from_ical(fh.read())

        for component in cal.walk():
            if component.name == "VEVENT":
                dt = component["DTSTART"].dt
                name = component["SUMMARY"].title()
                if dt > now.date():
                    print("Next bins are ", dt, name)
                    break
        
        # Assume those variables exist because I'm lazy
        bin_out_time = datetime(dt.year, dt.month, dt.day, 8, 0, 0)  # 8 am
        time_g.set(bin_out_time.timestamp())
        bin_i.info({"bin_type": name})

        sleep(120)
