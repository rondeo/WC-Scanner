# Faking RPi Board /!\
from util import context_finder as context
from util.logger import logger

from PIL import Image
import core.stepper_motor as st
import picamera
import subprocess
import json
import os


class Scanner:
    """
    Scanner class regroup components of the scanner
    Camera from the foundation Raspberry
    Stepper motor to drive the scanning platform
    """
    def __init__(self):
        """
        Constructor method,
        stepper motor configuration & bed state initialization
        """
        self.bed_rotation = 0
        self.bed_motor = st.StepperMotor(12, 6, 5, 200, 32)

    def on_ready(self):
        """
        Method use to notify users that the scanner is ready
        :return: None
        """
        self.turn_bed(360)
        self.turn_bed(-360)

    def turn_bed(self, degrees):
        """
        Apply a relative rotation of a certain degree
        negative number -> counter clockwise rotation
        positive number -> clockwise rotation
        :param degrees: degrees to apply to the bed (float)
        :return: None
        """
        if degrees > 0 :
            logger.info("Rotating bed of %.2f° clockwise", degrees)
        else:
            logger.info("Rotating bed of %.2f° counter clockwise", degrees)
        self.bed_motor.turn(degrees)

    def capture(self, path, name, width=3280, height=2464):
        """
        Can capture an image from the raspberry pi camera
        :param path: path where save the image
        :param name: name of the image
        :param width: width of the image
        :param height: height of the image
        :return: None
        """
        if context.running_on_raspberry:
            p = subprocess.Popen('raspistill -w {} -h {} -o {}/{}.jpg'.format(width, height, path, name), shell=True)
            p.wait()

        else:
            camera = picamera.PiCamera()
            im_shape = (height, width)
            bgr = picamera.array.PiRGBArray(camera, size=im_shape)
            camera.capture(path, name, "jpg")
            camera.close()
            img = Image.fromarray(bgr.array, 'L')
            img.save('{}/{}.jpg'.format(path, name))

    def loop_capture(self, project_name):
        """
        Starting a loop capture using the configuration file of the project
        A loop capture is a sequence of capture/turn_bed
        every x degrees we make a capture, this capture is saved in project's folder
        :param project_name: name of the project
        :return: None
        """
        project_path = '{}/{}'.format(context.__PROJECTS_PATH__, project_name)

        project_conf_f = open('{}/.project'.format(project_path), 'r')
        project_conf = json.load(project_conf_f)
        project_conf_f.close()
        # Project configuration loaded

        image_count = len(os.listdir(project_path)) - 1
        # -1 for config file

        ppr = int(project_conf['pict_per_rotation'])

        # Picture resolution [width, height]
        pres = list(map(int, project_conf['pict_res'].split('x')))

        bed_step = 360 // ppr
        for i in range(0, 361, bed_step):
            self.capture(project_path, image_count, pres[0], pres[1])
            self.turn_bed(bed_step)
            image_count += 1


if __name__ == "__main__":
    scanner = Scanner()
    scanner.on_ready()
