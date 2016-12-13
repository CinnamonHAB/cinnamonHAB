import oh2
import time

time.sleep(20)

oh2.SetAddr('openhab:8080')
oh2.Subscribe()
oh2.StartStream("demo", "0000")
