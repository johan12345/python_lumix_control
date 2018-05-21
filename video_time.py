from lumix_control import CameraControl
import xml.etree.ElementTree as ET
import datetime as dt
import tkinter as tk
import threading
import time

IP = ["192.168.1.100", "192.168.1.101"]
GH3 = [True, False]


def record_thread(statusvar, ip, gh3):
    control = CameraControl(ip)  # IP of camera
    control.start_camera_control()
    
    control.video_record_start()
    prev_remaining = dt.timedelta(hours=99)
    while not stop_event.is_set():
        try:
            state = ET.fromstring(control.get_state().text).find('state')
            remaining = dt.timedelta(seconds=int(state.find('video_remaincapacity').text))
            
            if gh3:
                should_restart = remaining > prev_remaining + dt.timedelta(minutes=1)
            else:
                rec = state.find('rec').text == 'on'
                should_restart = not rec or remaining < dt.timedelta(seconds=10)

            if should_restart:
                print('restarting record for {}'.format(ip))
                if not gh3: control.video_record_stop()
                control.video_record_start()

            statusvar.set('remaining: {}'.format(remaining))
            
            prev_remaining = remaining
        except:
            pass
        time.sleep(1)
    if not gh3: control.video_record_stop()


def stop_record():
    stop_event.set()
    thread.join()
    print('stopped')

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

v = [tk.StringVar()] * len(IP)
for i, ip in enumerate(IP):
    label1 = tk.Label(frame, text=ip)
    label1.grid(row=0, column=i)

    label2 = tk.Label(frame, textvariable=v[i])
    label2.grid(row=1, column=i)

stop_button = tk.Button(frame, text='Stop recording', command=stop_record)
stop_button.grid(row=2, column=0)

stop_event = threading.Event()

for ip, gh3, v in zip(IP, GH3, v):
    thread = threading.Thread(target=record_thread, args=(v,ip,gh3))
    thread.start()

root.mainloop()




