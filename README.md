# Mine-Scanner
This is a project which is meant to be used to create a 2D or 3D map of a space using LIDAR. There is multiple functions including callibrate, shot, 2D scan, 3D scan start, 3D scan stop. A program generation script is also included.
## Table of Contents
* [Program Generation](#program-generation)
* [Callibrate](#callibration)
* [Mapping](#mapping)
## Program Generation
Generating a program for the device is simple. This is done by running the file "ProgramGeneration.py", which is best done on a personal computer as opposed to the device. When the program is run it opens up a window with text boxes next to a "Set" button, followed by some text. The text indicates what the corresponding "Set" button and text box correspond to. The data is saved in a hierarchy as follows: Expedition > Section > Room , where in each higher class there can be multiple of a lower class within it. For instance one expedition can have two sections within it, where each section has four rooms within it. However, it is important to note that there can only ever be one expedition. After each time a new string is put into the text box the "Set" button should be pressed and the text on the right should update. Once a room has all of its data set the "Finish Room" button must be pushed and text under the "Finish Room" button will appear indicating that the information was saved. When all rooms are completed the "Save + Exit" button must be pushed. Then the program should exit and a new file should appear in the same folder as "ProgramGeneration.py" labeled outfile.json, this file is the finished program.

![alt text](https://github.com/Nacnud04/Mine-Scanner/blob/master/program_generator_window.png)

The expedition, station, and room characteristics are self explanatory. The stations characteristic includes the numbers of the stations located within the room. As of now there is only support for one station per room, therefore this number should increase by one for each room added to the expedition as station values do not reset back to 0 when a new section is added. Notes are the information which one could want to know when in the corresponding room. The neighbor direction is the angle from north at which the next room is at as seen from where the room is.
The data is formatted in JSON as such:
```
{
  "areas": [
    {
      "id": "R1", #Not user defined, automatically generated
      "section": "Section",
      "room": "room1",
      "stations": "1",
      "notes": "none",
      "neighborDirec": "180"
    }
  ]
}
```
## Mapping
When the program [MineScannerMain.py](https://github.com/Nacnud04/Mine-Scanner/blob/master/raspberry%20pi/MineScannerMain.py) is run, an 800 x 600 GUI appears. This is where all of the user actions are performed. On the left side there are six buttons each used to perform a function of the device. Then there are X, Y, and Z labels, and finally information about both the 2D and 3D active space.
### 2D Mapping
#### Callibration
Callibration is the first action which must be performed when a 2 dimensional scan is wanted. When the callibration button is pushed the Raspberry Pi sends a high value out of a GPIO pin which is then received by the Arduino Uno this tells the microcontroller to start callibrating. Callibration is done by finding the offset of the accelerometer, gyroscope, and magnetometer and then accounting for it in further calculations. Callibration for hard and soft iron has not been implemented yet. Once callibration is completed the callibration button no longer appears pressed down.
#### Shot
The shot function can be performed before or after the first 2D scan of a space. The shot function exists to let the device know where the next station is as compared to where it is now. It also provides the user a rough estimate as to where they are in relation to the other recorded stations in the form of a graph, and the XYZ labels. Once the shot function is called it creates a station (default name "Alley") and assigns it a number. After this the arduino shines a laser out the front of the device. This laser must be aligned with the next station, as where the laser appears is what the stations location is defined as. The user has 15 seconds to shine the laser at the station being recorded before data collection begins. Data collection begins by the arduino recording its angle in space. 15 accurate rotation mesaurements each are taken in quaternion form, followed by 30 distance mesaurements from the ultrasonic sensor. Then the "degree to position" function is called, which using rotation matricies calculated the exact place of the newly defined station in 3D space. Finally the "show" function is called which puts an image on the gui of where the stations are in 3d space. The red point is the first defined station, while the green point is the just recorded station. The grey points are stations which are neither the first nor last station.
#### 2D
This performs a scan of the space in 2D. First the RPLIDAR module is turned on via 4 npn transistors in parallel. Then the data about the room is read from the user created JSON file and some is displayed on the screen in the 2D column. Once the room has been created, data is immediately collected. If the user is in line with the horizontal plane of the LIDAR module, they will be detected as part of the room. This could lead to some weird results. Then an offset is added to the data, making the origin(0,0) of the data become equal to the active station in 2D space. Then rotation matricies are used to add a turn to the data depending on what angle the recording of the active station was facing. Meaning that a 2D scan of a room must be done with the device facing the same direction it was when the active stations position was recorded. Then the show function is performed, displaying what the recorded data looks like in scatterplot form, followed by what it looks like with the previous recorded data overlayed ontop. If the recorded room is the first room the first plot will appear blank. Finally the recorded data is written to the JSON file and the RPLIDAR module is turned off.
### 3D Mapping
A working version of 3D mapping a space has been developed, however it has yet to be posted and explained.
