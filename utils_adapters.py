from controlnet_aux.canny import CannyDetector    

def calc_canny_image(image, resolution=1024):
        condition_image = image
        canny_detector = CannyDetector()
            # Detect the canny map in low resolution to avoid high-frequency details
        condition_image = canny_detector(image, detect_resolution=384, image_resolution=resolution)
        print("Canny image detected")     
        return condition_image

def calc_sketch_image(self):
    ...
def calc_lineart_image(self):
    ...
def calc_depth_image(self):
    ...
def calc_openpose_image(self):
    ...