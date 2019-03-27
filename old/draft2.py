from datetime import datetime

# ts = '2019-03-27 15:59:41'
# ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# print(ts)
# print(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))


ts= "2018-02-12T09:22:02Z"
print(datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
