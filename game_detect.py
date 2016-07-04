import autoit
import ctypes
import datetime
import os
import sendgrid
import time

from sendgrid.helpers.mail import *


# Get screen size and properties
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
width, height = screensize
top_left_scan_box_x = int(width * 0.85)
top_left_scan_box_y = int(height * 0.15)
scan_width = int(width * 0.98) - top_left_scan_box_x
scan_height = top_left_scan_box_y - int(height * 0.02)

# Message box stuff
MessageBox = ctypes.windll.user32.MessageBoxW
MB_YESNO = 0x4
MB_ICONEXCLAMATION = 0x00000030
MB_CLICK_YES = 6
MB_CLICK_NO = 7

# Debug move mouse around search area to see where it's earching
# bottom_left_scan_box_x = int(width * 0.85)
# bottom_left_scan_box_y = int(height * 0.15)
# top_right_scan_box_x = int(width * 0.98)
# top_right_scan_box_y = int(height * 0.02)
# for _ in range(3):
#     autoit.mouse_move(bottom_left_scan_box_x, bottom_left_scan_box_y)
#     autoit.mouse_move(top_right_scan_box_x, top_right_scan_box_y)


# Blue "leave game" color #3c92cb
red = 0x3c
green = 0x92
blue = 0xcb


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def msg_box(text="Do push ups!"):
    result = MessageBox(None, text, 'Tren hard go pro', MB_ICONEXCLAMATION | MB_YESNO)
    if result == MB_CLICK_YES:
        output = "GG yo"
    else:
        output = "FAIL"
    open('results.txt', 'a').write("{}\n".format(output))


def count_success():
    return open('results.txt').readlines().count('GG yo\n')


def count_fail():
    return open('results.txt').readlines().count('FAIL\n')


def send_email(file_name):
    SENDGRID_API_KEY = None
    assert SENDGRID_API_KEY, "You need to set SENGRID_API_KEY!"
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email("eric@ckcollab.com")
    subject = "Overwatcher alert"
    to_email = Email("booj2600@gmail.com")
    content = Content("text/plain", "Here are your results:\n{}".format(open(file_name).read()))
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())


def do_result_dump():
    day_of_week = datetime.datetime.today().weekday()
    if day_of_week == 0:  # 0 is monday
        # It's monday, save logs
        current_date_string = datetime.datetime.today().strftime("%d-%m-%y")
        file_name = "results-{}.txt".format(current_date_string)
        with open(file_name, 'w') as output:
            output.write("Success={}\n".format(count_success()))
            output.write("Fail={}\n".format(count_fail()))

        # we counted our stuff, remove it
        os.remove("results.txt")

        # email it
        send_email(file_name)


# -----------------------------------------------------------------------------
# State checks
# -----------------------------------------------------------------------------
def check_if_at_leave_screen():
    hits = 0
    for x in range(top_left_scan_box_x, top_left_scan_box_x + scan_width, 10):
        for y in range(top_left_scan_box_y, top_left_scan_box_y - scan_height, -10):
            pixel = hex(autoit.pixel_get_color(x, y))
            if pixel and pixel != hex(0):
                pixel_r, pixel_g, pixel_b = int(pixel[2:4], 16), int(pixel[4:6], 16), int(pixel[6:8], 16)  # skip 0x in front

                pixel_r_in_tolerance = red * 0.9 < pixel_r < red * 1.1
                pixel_g_in_tolerance = green * 0.9 < pixel_g < green * 1.1
                pixel_b_in_tolerance = blue * 0.9 < pixel_b < blue * 1.1

                if pixel_r_in_tolerance and pixel_g_in_tolerance and pixel_b_in_tolerance:
                    hits += 1
    return hits > 10


def check_if_overwatch_is_running():
    return autoit.process_exists('Overwatch.exe')


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        if check_if_overwatch_is_running():
            if check_if_at_leave_screen():
                msg_box()

        time.sleep(1)

