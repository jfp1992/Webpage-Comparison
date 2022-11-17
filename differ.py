""" Based on code from Olivier Bénard @ https://github.com/olivierbenard/differences-between-two-images
"""
from cv2 import cv2
import numpy as np
from pathlib import Path
import warnings

from custom_logging import xlogging

warnings.filterwarnings("ignore", category=UserWarning)  # ignore UserWarning
try:
    from skimage.measure import compare_ssim as ssim  # compare_ssim fully deprecated in version 0.18
except ImportError:
    from skimage.metrics import structural_similarity as ssim


class Differences:
    def __init__(self, images):
        self.images = images
        if not isinstance(self.images, list):
            raise ValueError("images should be a list")
        else:
            if len(self.images) < 1:
                raise ValueError("images list should contain more than 1 image")

        # ref_frame
        self.initialized = False
        self.ref_name = None
        self.ref_frame = None
        self.ref_grey_frame = None
        self.ref_h = None
        self.ref_w = None

        # com_frame
        self.com_name = None
        self.com_frame = None
        self.com_grey_frame = None
        self.com_h = None
        self.com_w = None

    def check_height(self, image):
        if self.ref_h == self.com_h:
            xlogging(2, f"{self.ref_name} is the same height {self.com_name}")

        # bottom
        elif self.ref_h < self.com_h:
            xlogging(2, f"Adding {self.com_h - self.ref_h} pixels to the bottom of reference {self.ref_name}")
            self.ref_frame = cv2.copyMakeBorder(self.ref_frame, 0, self.com_h - self.ref_h, 0, 0, 0)
            cv2.imwrite(image, self.ref_frame)
            self.ref_frame = cv2.imread(image)
            self.ref_grey_frame = cv2.cvtColor(self.ref_frame, cv2.COLOR_BGR2GRAY)

        elif self.com_h < self.ref_h:
            xlogging(2, f"Adding {self.ref_h - self.com_h} pixels to the bottom of comparison {self.com_name}")
            self.com_frame = cv2.copyMakeBorder(self.com_frame, 0, self.ref_h - self.com_h, 0, 0, 0)
            cv2.imwrite(image, self.com_frame)
            self.com_frame = cv2.imread(image)
            self.com_grey_frame = cv2.cvtColor(self.com_frame, cv2.COLOR_BGR2GRAY)

    def check_width(self, image):
        if self.ref_w == self.com_w:
            xlogging(2, f"{self.ref_name} is the same height {self.com_name}")

        # right
        elif self.ref_w < self.com_w:
            xlogging(2, f"Adding {self.com_w - self.ref_w} pixels to the right of reference {self.ref_name}")
            self.ref_frame = cv2.copyMakeBorder(self.ref_frame, 0, 0, 0, self.com_w - self.ref_w, 0)
            cv2.imwrite(image, self.ref_frame)
            self.ref_frame = cv2.imread(image)
            self.ref_grey_frame = cv2.cvtColor(self.ref_frame, cv2.COLOR_BGR2GRAY)

        elif self.com_w < self.ref_w:
            xlogging(2, f"Adding {self.ref_w - self.com_w} pixels to the right of comparison {self.com_name}")
            self.com_frame = cv2.copyMakeBorder(self.com_frame, 0, 0, 0, self.ref_w - self.com_w, 0)
            cv2.imwrite(image, self.com_frame)
            self.com_frame = cv2.imread(image)
            self.com_grey_frame = cv2.cvtColor(self.com_frame, cv2.COLOR_BGR2GRAY)

    def compare(self):
        num_img = len(self.images)
        if num_img == 0:
            xlogging(2, "Images files must be specified")
            return
        if num_img < 2:
            xlogging(2, "Image of reference must be compared with, at least, one another image")
            return

        for image in self.images:
            self.com_name = Path(image).stem
            self.com_frame = cv2.imread(image)
            self.com_grey_frame = cv2.cvtColor(self.com_frame, cv2.COLOR_BGR2GRAY)

            if not self.initialized:
                xlogging(2, f"{self.com_name} taken as reference")
                self.ref_name = self.com_name
                self.ref_frame = self.com_frame
                self.ref_grey_frame = self.com_grey_frame
                self.ref_h = self.ref_frame.shape[0]
                xlogging(2, f"ref frame height: {self.ref_frame.shape[0]}")
                self.ref_w = self.ref_frame.shape[1]
                xlogging(2, f"ref frame width: {self.ref_frame.shape[1]}")
                self.initialized = True
            else:
                self.com_h = self.com_frame.shape[0]
                xlogging(2, f"com frame height: {self.com_frame.shape[0]}")
                self.com_w = self.com_frame.shape[1]
                xlogging(2, f"com frame width: {self.com_frame.shape[1]}")

                self.check_height(image)
                self.check_width(image)

                (score, diff) = ssim(self.ref_grey_frame, self.com_grey_frame, full=True)
                xlogging(2, f"Similarity between {self.ref_name} and {self.com_name}: {score}")
                if score == 1:
                    xlogging(2, "Reference and comparison are identical.")
                    return

                diff = (diff * 255).astype("uint8")
                retval, thresh = cv2.threshold(diff, 127, 255, cv2.THRESH_BINARY_INV)
                contours, hirarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                temp_ref_frame = self.ref_frame.copy()
                filled_after = self.ref_frame.copy()
                mask = np.zeros(temp_ref_frame.shape, dtype="uint8")

                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 40:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(temp_ref_frame, (x, y), (x + w, y + h), (36, 255, 12), 2)
                        cv2.rectangle(self.com_frame, (x, y), (x + w, y + h), (36, 255, 12), 2)
                        cv2.drawContours(mask, [contour], 0, (0, 255, 0), -1)
                        cv2.drawContours(filled_after, [contour], 0, (0, 255, 0), -1)

                xlogging(2, f"Saving reference {self.ref_name}")
                cv2.imwrite(f"output/a_{self.ref_name}.png", temp_ref_frame)

                xlogging(2, f"Saving comparison {self.com_name}")
                cv2.imwrite(f"output/a_{self.com_name}.png", self.com_frame)
                return
