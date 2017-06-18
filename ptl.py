#!/usr/bin/env python3

import argparse
import signal
import sys
import os
from cv2 import VideoCapture, imwrite, IMWRITE_PNG_COMPRESSION, IMWRITE_JPEG_QUALITY, IMWRITE_WEBP_QUALITY,\
    CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH
from time import sleep


class TimeLapse:

    def __init__(self, config):
        """__init__(self):"""
        self.interval = config.interval
        self.shots = config.shots
        self.output = config.output
        self.camera = VideoCapture(config.device)
        self.shots = config.shots
        self.currnetShot = 0
        self.imageName = config.name
        self.imageType = config.type
        self.imageQuality = config.quality
        self.verbose = config.verbose

    def getResolution(self):
        """getResolution"""
        width = self.camera.get(CAP_PROP_FRAME_WIDTH)
        height = self.camera.get(CAP_PROP_FRAME_HEIGHT)
        return width, height

    def setMaxResolution(self):
        """setMaxResololution"""
        self.setResolution(10000, 10000)

    def setResolution(self, width, height):
        """setMaxResolution"""
        self.camera.set(CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(CAP_PROP_FRAME_HEIGHT, height)

    def run(self):
        """run"""
        while True:
            if self.shots and self.shots <= self.currnetShot:
                break
            ok, img = self.takePhoto()
            if ok:
                self.saveImage(img)
                self.currnetShot += 1
            sleep(self.interval)

    def takePhoto(self):
        """takePhoto"""
        return self.camera.read()

    def saveImage(self, img):
        """saveImage"""
        name = '{name}_{index:02d}.{type}'.format(name=self.imageName,
                                                  index=self.currnetShot,
                                                  type=self.imageType)
        imagePath = os.path.join(self.output, name)
        if self.verbose:
            print('Save a photo {} to: {}'.format(img.shape, imagePath))

        imwrite(imagePath, img, self.imageOpts())

    def imageOpts(self):
        if self.imageType == 'jpg':
            if self.imageQuality < 0 or self.imageQuality > 100:
                self.imageQuality = 95
            return IMWRITE_JPEG_QUALITY, self.imageQuality
        elif self.imageType == 'png':
            if self.imageQuality < 0 or self.imageQuality > 9:
                self.imageQuality = 3
            return IMWRITE_PNG_COMPRESSION, self.imageQuality
        elif self.imageType == 'webp':
            if self.imageQuality < 0 or self.imageQuality > 100:
                self.imageQuality = 95
            return IMWRITE_WEBP_QUALITY, self.imageQuality

    def stop(self):
        """stop"""
        self.shots = self.currnetShot

    def __del__(self):
        self.camera.release()


def stop_program(signal, frame):
    """stop_program"""
    print('\nPrograms stop on next photo')
    tl.stop()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop_program)
    parser = argparse.ArgumentParser(usage='%(prog)s [options]')
    parser.add_argument('-v', '--verbose', action="store_true", help="verbose")
    parser.add_argument('-i', '--interval', default=1, type=int, help='time interval in sec [default = 1]')
    parser.add_argument('-d', '--device', default=0, type=int, help='Device number [default = 0]')
    parser.add_argument('-s', '--shots', type=int, help='Number of shots to take')
    parser.add_argument('-n', '--name', type=str, default='image', help='Base name of taken photos ')
    parser.add_argument('-t', '--type', choices=['jpg', 'png', 'webp'], default='jpg', help='Image type')
    parser.add_argument('-q', '--quality', type=int, default=-1, help='Image quality jpg 0-100, webm 0-100, png 9-0')
    parser.add_argument('-o', '--output', default=".", type=str,
                        help='Output directory for captured images [default = ./ ]')
    config = parser.parse_args()
    tl = TimeLapse(config)
    print('Press Ctrl+C to stop')
    tl.setMaxResolution()
    tl.run()
