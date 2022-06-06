# Bachelor Thesis
## Nic Grogg

This thesis is a complete pipeline from creating a hardware setup to detecting object with this setup. The main goal here was to...

## CAD

In the subfolder of the CAD there are ...

## Blender

In this folder there are the files for the creation of artificial images to train our neural network. When the pipeline for this thesis was set out, the decision was made to try to detect a toy car that was previously used for another thesis at the pd|z lab. Thus the object to detect and make artificial images of is this toy car.

### Requirements

This project was done with Blender version 3.1.2. No additional packages are needed for the Blender Python script, it should run as is.

### Creating Artificial Images:

As mentioned before the object I am trying to detect is a small toy car. Since the car was previously used in another Thesis at the pd|z lab there existed a 3D scan and a blender compatible object file of it which is stored in the Blender -> Objects -> Car sub folder. For the surrounding scene, the framework created in NX12, described in the [CAD folder](##-cad), is used.

To make artificial images of the car in this scene, open the blender file "CameraSetup.blend" and go to the Scripting tab at the top. This will open the python script in Blender where the amount of random camera position changes and the amount of images rendered for each position can be set with the "total_position_changes" and "total_render_count" variables. After setting the desired values, the script can be executed and the images for each object will be created and saved to the data/Blender/images folder. Further, the Blender python script outputs labels for each image as text files, which are saved in the data/Blender/labels folder. These text files are formatted so that the [yolov5 neural network](https://github.com/ultralytics/yolov5) can be trained on them. A text file contains the class of the object, the x and y coordinates of the center, the width and the height of the bounding box. In addition to these text files an additional text file which contains the possible classes is in the data/Blender/labels folder in order to properly train the [yolov5 neural network](https://github.com/ultralytics/yolov5). To visualize the bounding box, the "DrawBoundingBox.py" script is provided.

### Adding New Objects:

If you want to add new objects, here's how to properly import them into the Blender scene:

1. First you need to create or download the object as a Blender file or Blender compatible file.
2. After the first step, open the Blender "river.blend" file.
3. In the upper right corner there is a ViewLayer window where you can see the scene collection and within it the collections of objects present in this scene. If you want to add a new object, select the "trash_objects" collection in this window.
4. There are two ways to add an object to the Blender file. a) You have saved the object as a Blender compatible file, but not as a Blender file itself, or b) You want to extract the object from another Blender file.
   - a) Go to File -> import -> "filetype" and select the object file you want to import.
   - b) Go to File -> append -> "open the blender file" -> Object -> select the file you want to import.
5. Sometimes the imported objects consist of several parts. For the script to work properly, the parts must be combined into one object. To do this, go to the Layout tab at the top and select each part with Shift + left click. After selecting all the parts, press ctrl + j and they will be joined into one object, which is now listed in the "trash_objects" collection. If you run the script now, the images for these objects will be automatically rendered.

## Train the Yolov5 Network

...

## Calibrating the Cameras

...

## Object Detection and Depth Estimation

...
