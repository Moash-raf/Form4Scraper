from datetime import datetime

timestamp1 = "2025-10-22T08:54:34-04:00"
timestamp2 = "2025-10-21T08:54:34-04:00"
timestamp1 = timestamp1.replace("Z", "+00:00")
ts_datetime_object = datetime.fromisoformat(timestamp1)

format_string = "%Y-%m-%dT%H:%M:%S"

# datetime_object1 = datetime.strptime(timestamp1, format_string)
# datetime_object2 = datetime.strptime(timestamp2, format_string)

if ts_datetime_object.date() == datetime.today().date():
    print("works")

# if datetime_object2.date() == datetime.today().date():
#     print("nope")
