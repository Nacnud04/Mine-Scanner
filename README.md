# Mine-Scanner
This is a project which is meant to be used to create a 2D or 3D map of a space using LIDAR. There is multiple functions including callibrate, shot, 2D scan, 3D scan start, 3D scan stop. A program generation script is also included.
## Table of Contents
* [Program Generation](#program-generation)
* [Callibrate](#callibrate)
## Program Generation
Generating a program for the device is simple. This is done by running the file "ProgramGeneration.py", which is best done on a personal computer as opposed to the device. When the program is run it opens up a window with text boxes next to a "Set" button, followed by some text. The text indicates what the corresponding "Set" button and text box correspond to. The data is saved in a hierarchy as follows: Expedition > Section > Room , where in the higher class there can be multiple of a lower class within it. For instance one expedition can have two sections within it, where each section has four rooms within it. However there can only ever be one expedition. After each time a new string is put into the text box the "Set" button should be pressed and the text on the right should update. Once a room has all of its data set the "Finish Room" button must be pushed and text under the "Finish Room" button will appear indicating that the information was saved. When all rooms are completed the "Save + Exit" button must be pushed. Then the program should exit and a new file should appear in the same folder as "ProgramGeneration.py" labeled outfile.json, this file is the finished program.
The expedition, station, and room characteristics are self explanatory. The stations characteristic includes the numbers of the stations located within the room. As of now there is only support for one station per room, therefore this number should increase by one for each room added to the expedition as station values do not reset back to 0 when a new section is added. Notes are the information which one could want to know when in the corresponding room. The neighbor direction is the angle from north at which the next room is at as seen from where the room is.
The data is formatted as such:
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
## Functions
### Callibrate
This callibrates the 6 axis position sensing system. This is necessary for accurate function of the device. Callibration for hard and soft iron sources will be added in the future.
###
