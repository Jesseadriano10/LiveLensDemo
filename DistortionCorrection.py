import numpy as np
import cv2 as cv
from google.colab.patches import cv2_imshow
from numpy import asarray
from PIL import Image
from google.colab.patches import cv2_imshow

"""
# Usage
if __name__ == "__main__":
    image_dir = 'path_to_images'  # Replace with your images directory
    # grabs all da files, glob style  ;)
    # Jank but works, "Files" is not the shared "Files" folder on the drive but a shortcut in my personal drive to the shared capstone Files folder
    image_paths = glob.glob(f'{image_dir}/*.JPG')
    images = CameraCalibrator.load_images(image_paths)
    calibrator = CameraCalibrator(chessboard_edges=(9, 6), image_dimensions=(4032, 2268))
    mtx, dist = calibrator.calibration_parameters(images)
    test_image = images[0]
    corrected_img, cropped_img = calibrator.distortion_correction(test_image)
    cv2.imshow('Corrected Image', corrected_img)
    cv2.imshow('Cropped Image', cropped_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
"""
class DistortionCorrection:
    def __init__(self, chessboardEdges, image_dimensions):
        self.chessboard_edges = chessboardEdges
        self.image_dimensions = image_dimensions
        self.mtx = None
        self.dist = None
    
    def calibration_parameters(self, input_images):
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objp = np.zeros((self.chessboard_edges[0]*self.chessboard_edges[1],3), np.float32)
        ojbp[:,:2] = np.mgrid[0:self.chessboard_edges[0], 0:self.chessboard_edges[1]].T.reshape(-1,2)
        objpoints = []
        imgpoints = []
        
        for image in input_images:
            gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            ret, corners = cv.findChessboardCorners(gray, self.chessboard_edges, None)
            if ret:
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners2)
        
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        self.mtx, self.dist = mtx, dist
        return mtx, dist
    """
        distortion_correction takes an input image and remaps the pixels based on the distortion parameters   
        Inputs:
        - img: the input image
        - ret, mtx, dist: calibration parameters from the calibration_parameters function necessary to remap distorted images
        Outputs:
        - corrected_img: the remapped image without a cropped edge
        - cropped_img: the remapped image with a cropped edge
    """
    def distortion_correction(self, img):
        h, w = img.shape[:2]
        new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(self.mtx, self.dist, (w,h), 1, (w,h))
        # undistort
        corrected_img = cv.undistort(img, self.mtx, self.dist, None, new_camera_matrix)
        # crop the image
        x, y, w, h = roi
        cropped_img = corrected_img[y:y+h, x:x+w]
        return corrected_img, cropped_img

    def load_images(self, image_paths):
        images = []
        for path in image_paths:
            img = cv.imread(path)
            if img is not None:
                images.append(img)
        return images