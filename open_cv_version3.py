# -*- coding: utf-8 -*-
"""Open_CV_Version3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ek0eaJjj9yjWrneDCA3qSCZjNSmQL_SI

# Initialization
"""

!pip install google-colab
!pip install Pillow

import numpy as np
import cv2 as cv
from google.colab.patches import cv2_imshow
from numpy import asarray
from PIL import Image
from google.colab.patches import cv2_imshow

#Only neccessary for testing, not actually used in any of the functions
from google.colab import drive
drive.mount('/content/drive')
import glob

"""#Function definition for getting calibration parameters"""

#input jpgs directly

def calibration_parameters_v2(input_images,chessboardEdges,imagedimensions):
    #function for getting the calibration parameters based on images of the checkerboard pattern

    #_______________________________________________________________________________________________________________
    #Inputs:
    #input_image_paths, an array of the input images

    #chessboardEdges, a 2 entry tuple based on the number of white-black edges not including the outside
    #edges for horizontal and vertical dimensions respetively, ie chessboardEdges = (9,6) corresponds to a 9 wide and 6 tall pattern

    #imagedimensions, a 2 entry tuple based on pixel dimensions of images

    #_______________________________________________________________________________________________________________
    #Outputs:
    #mtx, dist are returned using a return statement and used as inputs for the distortion_correction function

    #_______________________________________________________________________________________________________________


    # termination criteria, default OpenCV settings for finding corners of the chessboard
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    #Prepare object points
    #Initializes arrays for distortion mapping
    objp = np.zeros((chessboardEdges[0] * chessboardEdges[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboardEdges[0],0:chessboardEdges[1]].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    for image in input_images:

        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # Find the chess board corners for each image
        ret, corners = cv.findChessboardCorners(gray, chessboardEdges, None)

        # If found, add object points, image points (after refining them)
        if ret == True:

            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
            #imgpoints.append(corners) don't know why but the tutorial video I watched had this line of code instead of the previous line which is from the OpenCV exmple

            # Draw and display the corners
            cv.drawChessboardCorners(image, chessboardEdges, corners2, ret)
            cv.waitKey(1000)

    cv.destroyAllWindows()

    #_______________________________________________________________________________________________________________
    #This one line of code returns the camera matrix, distortion coefficients, rotation vectors, and translation vectors
    #With those images can be undistorted
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


    #_______________________________________________________________________________________________________________
    #Error calculation, uncomment to have error of calibration printed when function is run
    """mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error
    print( "total error: {}".format(mean_error/len(objpoints)) )"""

    return mtx, dist

"""#Function definition for correcting an images distortion

"""

def distortion_correction(img, mtx, dist):
  #distortion_correction taks an input image and remaps the pixels based on the distortion parameters
  #_______________________________________________________________________________________________________________

  #Inputs:
  #img_path, the input image
  #ret, mtx, dist are some of the calibration parameters from the calibration_parameters function neccessary to remap distorted images
  #_______________________________________________________________________________________________________________

  #Outputs:
  #corrected_img, the remapped image without a cropped edge
  #cropped_img, the remapped image with a cropped edge
  #_______________________________________________________________________________________________________________

  h,  w = img.shape[:2]
  newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

  # undistort
  corrected_img = cv.undistort(img, mtx, dist, None, newCameraMatrix)
  # crop the image
  x, y, w, h = roi
  cropped_img = corrected_img[y:y+h, x:x+w]

  #_______________________________________________________________________________________________________________

  return corrected_img, cropped_img

"""#Testing"""

#grabs all da files, glob style  ;)
#Jank but works, "Files" is not the shared "Files" folder on the drive but a shortcut in my personal drive to the shared capstone Files folder
image_paths = glob.glob('drive/MyDrive/Files/Batch_4/*.JPG')
image_list = []

for path in image_paths:
  img = cv.imread(path)
  img = np.array(img)
  image_list.append(img)

#cv2_imshow(image_list[0])
print(image_list[0].size)
#print(image_array)
chessboardEdges = (9,6)             #based on the number of white-black edges not including outside edges for horizontal and vertical dimensions respetively
imagedimensions = (4032,2268)       #pixel dimensions of images, iphone JPG are 3024 x 4023

mtx, dist = calibration_parameters_v2(image_list,chessboardEdges,imagedimensions)
test_image = cv.imread(image_paths[0])
corrected_img, cropped_img = distortion_correction(test_image, mtx, dist)
cv2_imshow(corrected_img)
cv2_imshow(cropped_img)

print(mtx)
print(dist)
cv2_imshow(corrected_img)