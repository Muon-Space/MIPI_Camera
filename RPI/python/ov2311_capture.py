import arducam_mipicamera as arducam
import v4l2 #sudo pip install v4l2
import time
import numpy as np
import cv2 #sudo apt-get install python-opencv
import math
def align_down(size, align):
    return (size & ~((align)-1))

def align_up(size, align):
    return align_down(size + align - 1, align)

# All register stuff is pulled from https://github.com/ArduCAM/ArduCAM_USB_Camera_Shield/commit/1a5ddf36ba80ed7d5a449c2c3a971363df340c91
def set_exposure_ms(camera, t):
    #exp = int(math.floor(t * 1000*1000 / (1e9 * 904 / 80000000)))
    #camera.write_sensor_reg(0x3501, (exp & 0xFF00) >> 8)
    #camera.write_sensor_reg(0x3502, (exp & 0x00FF) >> 0)
    camera.set_control(v4l2.V4L2_CID_EXPOSURE, t*10)
    print("Exposure set to %.1f ms" % t)

def set_gain_db(camera, g):
    camera.write_sensor_reg(0x3508, int(g) & 0x001F)
    print("0x3508: 0x%08x" % (fine_gain))

def set_analog_gain(camera, g):
    coarse_gain = int(math.floor(g / 100))
    fine_gain = int(math.floor((g / 100) % 1 * 100))
    camera.write_sensor_reg(0x3508, coarse_gain)
    camera.write_sensor_reg(0x3509, fine_gain)
    print("0x3508: 0x%08x, 0x3509: 0x%08x" % (coarse_gain, fine_gain))

def set_fps(camera, fps):
    vts = int(math.floor(80000000 / (936 * fps)))
    camera.write_sensor_reg(0x380E, (vts & 0xFF00) >>8)
    camera.write_sensor_reg(0x380F, (vts & 0x00FF) >>0)
    print("0x380E: 0x%08x, 0x380F: 0x%08x" % ((vts & 0xFF00) >>8, 
                                              (vts & 0x0FF)>>0))

def set_controls(camera):

    try:
        #camera.software_auto_exposure(enable = True)
        #exp = int(math.floor(exposure_us * 1000 / (1e9 * 904 / 80000000)))
        #print("Exposure reg val: %d" % exp)
        #camera.write_sensor_reg(0x3501, (exp & 0xFF00) >> 8)
        #camera.write_sensor_reg(0x3502, (exp & 0x00FF) >> 0)
        set_exposure_ms(camera,10)
    except Exception as e:
        print(e)
if __name__ == "__main__":
    outfldr = "out"
    try:
        camera = arducam.mipi_camera()
        print("Open camera...")
        camera.init_camera()
        camera.set_mode(6) # chose a camera mode which yields raw10 pixel format, see output of list_format utility
        fmt = camera.get_format()
        width = fmt.get("width")
        height = fmt.get("height")
        print("Current resolution is {w}x{h}".format(w=width, h=height))

        set_controls(camera)
        set_fps(camera, 1)
        set_analog_gain(camera, 1000)
        set_exposure_ms(camera, 10)

         
        time.sleep(1)
        i = 0
        while cv2.waitKey(10) != 27:
            frame = camera.capture(encoding = 'raw')
            #height = fmt[1]
            #width  = fmt[0]
            frame = arducam.remove_padding(frame.data, width, height, 10)
            frame = arducam.unpack_mipi_raw10(frame)
            frame = frame.reshape(height, width) << 6
            image = frame
            #image = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)
            cv2.imshow("Arducam", image)
            #cv2.imwrite("%s/%d.png" % (outfldr, i), image)
            i += 1
            #set_exposure_ms(camera, i*10)
            #break

        # Release memory
        del frame
        # print("Stop preview...")
        # camera.stop_preview()
        print("Close camera...")
        camera.close_camera()
    except Exception as e:
        print(e)
