from datetime import timedelta, datetime #timedelta is a Python class used to represent a duration of time 


def parse_duration(duration_str):

    duration_str = duration_str.replace("P", "").replace("T", "") #method chaining   

    components = ["D", "H", "M", "S"]
    values = {"D": 0, "H": 0, "M": 0, "S": 0}

    for component in components:
        if component in duration_str:
            value, duration_str = duration_str.split(component) #spliting the components
            values[component] = int(value) #overwriting the dictionary

    total_duration = timedelta(
        days=values["D"], hours=values["H"], minutes=values["M"], seconds=values["S"] #now represents the dictionary as time  
    )

    return total_duration


def transform_data(row):

    duration_td = parse_duration(row["Duration"])

    row["Duration"] = (datetime.min + duration_td).time() #datetime.min is the earliest value that is 00.00.00 and extracting the time component

    row["Video_Type"] = "Shorts" if duration_td.total_seconds() <= 60 else "Normal"

    return row