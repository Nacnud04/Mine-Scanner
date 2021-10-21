import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
gpio.setup(26, gpio.OUT)

gpio.output(26, gpio.HIGH)