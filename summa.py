from datetime import datetime
start_time = datetime.now()
print("Hi")
end_time = datetime.now()
time_taken = (end_time - start_time).seconds
print(time_taken)