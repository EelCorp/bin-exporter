from datetime import datetime
from time import sleep
from typing import Dict
import requests

from icalendar import Calendar
from prometheus_client import Gauge, start_http_server

class UnableToGetBinCalendar(Exception):
    """Unable to get the bin calender."""


def get_ical(uprn: str) -> Calendar:
    res = requests.post(
        "https://www.southampton.gov.uk/whereilive/waste-calendar",
        params={"UPRN": uprn},
        data={
            "ddlReminder": 0,
            "btniCal": None,
            "ufprt": "CC6F39967216660AE23AE6C3B4FAC9516CA477C34B95F1D02B495A7A42B9AE4CE3C27400929199B9D8DDACBD674875FB4B85F510982C8937C95365FFB259FD71E956CC28E104953693D57A4EE67565D47E713D0D34EFA513EF396D63246D51A6623E9C43CBE85E4F555EC714965DFE4697FB727AFACF1F6F4D2C7CC77C03471402B5BCF14E148B16CC4ECD3DAC761429D84A164C65F5A764453A24B0D882BBD138BBE24864A685D299D025DCB68E654E"
        }
    )

    if res.status_code != 200:
        raise UnableToGetBinCalendar(f"Unable to fetch calendar: Error {res.status_code}")

    calendar = Calendar.from_ical(res.content.decode())
    
    if len(calendar.walk()) == 0:
        raise UnableToGetBinCalendar("Got no events. Is the UPRN valid?")
    
    return calendar
    

if __name__ == "__main__":
    uprn = 10034867179 
    time_g = Gauge('bins_time_next', 'Next time the bins need to go out', ['uprn', 'bin_type'])

    start_http_server(4444)

    while True:
        now = datetime.now()

        try:
            cal = get_ical(uprn)

            next_bin_type: Dict[str, datetime] = {}

            for component in cal.walk():
                if component.name == "VEVENT":
                    dt = component["DTSTART"].dt
                    name = component["SUMMARY"].title()
                    if dt > now.date() and name not in next_bin_type:
                        next_bin_type[name] = dt
            
            for bin_type, dt in next_bin_type.items():
                # 6:30 am is the earliest time the council will come
                bin_out_time = datetime(dt.year, dt.month, dt.day, 6, 30, 0)
                time_g.labels(uprn, bin_type).set(bin_out_time.timestamp())
        except UnableToGetBinCalendar as e:
            print(e)

        sleep(120)
