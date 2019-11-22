import os
import uuid
from typing import Iterable, List

import numpy as np
from skimage import io
from sklearn import feature_extraction

from Explorer import Explorer


class Converter:
    def __init__(self, explorer: Explorer, patch_size: int,
                 max_patches_per_image: int):
        self.explorer = explorer
        self.patch_size = patch_size
        self.max_patches_per_image = max_patches_per_image

        self.explorer.create_output_folders()
        self.images_and_masks_paths = self.explorer.get_images_and_masks_paths(
        )
        self.images_output_paths = [
            path for path in explorer.image_classes_paths
        ]

    def process_images(self) -> None:
        # Background path is common to all classes.
        background_path = self.explorer.background_path

        # Process all classes
        for path in self.images_and_masks_paths:
            print('Processing path: %s.' % path[0])
            images_path = path[0]
            masks_path = path[1]
            class_name = self.explorer.extract_class_name(images_path)

            # Path for saving the foreground for this class
            foreground_path = self.explorer.get_output_path_for_class(
                self.images_output_paths, class_name)

            for collection in self._yield_images_masks_patches(
                    images_path, masks_path):
                image_patches = collection[0]
                mask_patches = collection[1]

                for image_mask_pair in zip(image_patches, mask_patches):
                    # Right now just save the output image as jpg
                    filename = uuid.uuid4().hex + '.jpg'
                    self._classify_and_save_patch(image_mask_pair[0],
                                                  image_mask_pair[1], filename,
                                                  foreground_path,
                                                  background_path)

    def _yield_images_masks_patches(self, images_path: str,
                                    masks_path: str) -> Iterable:
        """
        Returns an iterable composed by a pair of image and patches, whose 
        number is specified by _extract_patches.
        """
        pairs = self.explorer.yield_image_mask_filename_pair(
            images_path, masks_path)
        for pair in pairs:
            image = io.imread(pair[0])
            mask = io.imread(pair[1], as_gray=True)
            try:
                [image_patches,
                 mask_patches] = self._extract_patches(image, mask)
                yield [image_patches, mask_patches]
            except ValueError:
                # Patch is too big. Ignoring image to have fixed dimension patches.
                print('Patch size is too big for image: ', pair[0])

    def _extract_patches(self, image: np.ndarray,
                         mask: np.ndarray) -> List[np.ndarray]:
        """
        Returns a list of image and mask patches, using the same random_state
        to extract corresponding patches. This allows to use the patch's mask
        to classify the image patch itself as foreground or background. 
        """
        try:
            image_patches = feature_extraction.image.extract_patches_2d(
                image, (self.patch_size, self.patch_size),
                max_patches=self.max_patches_per_image,
                random_state=23)
            mask_patches = feature_extraction.image.extract_patches_2d(
                mask, (self.patch_size, self.patch_size),
                max_patches=self.max_patches_per_image,
                random_state=23)
        except ValueError:
            raise ValueError("Patch is too big.")

        return [image_patches, mask_patches]

    def _is_mask_black(self, mask: np.ndarray) -> bool:
        """
        Returns true if the active part of the mask (for example a person in a 
        pedestrian detection problem) is black, false otherwise.
        """
        total_pixels = mask.size
        white_pixels = np.count_nonzero(mask)
        black_pixels = total_pixels - white_pixels

        return white_pixels > black_pixels

    def _patch_belongs_to_foreground(self,
                                     mask: np.ndarray,
                                     is_mask_black: bool,
                                     percentage_threshold: float = 1e-2
                                     ) -> bool:
        """
        Classify an image based on its patch. If there are more than a set 
        percentage of active pixels, the image is considered part of the
        foreground otherwise part of the background.
        """

        if np.unique(mask).size > 1:
            if not (0 in np.unique(mask) and 255 in np.unique(mask)):
                raise ValueError('Mask must be binary')

        total_pixels = mask.size
        white_pixels = np.count_nonzero(mask)
        black_pixels = total_pixels - white_pixels

        active_pixels = black_pixels if is_mask_black else white_pixels

        return active_pixels > percentage_threshold

    def _classify_and_save_patch(self, image: np.ndarray, mask: np.ndarray,
                                 filename: str, foreground_path: str,
                                 background_path: str) -> None:
        """
        Saves an image patch to the correct output folder.
        """
        patch_belongs_to_foreground = self._patch_belongs_to_foreground(
            mask, self._is_mask_black(mask))

        if patch_belongs_to_foreground:
            io.imsave(os.path.join(foreground_path, filename), image)
        else:
            io.imsave(os.path.join(background_path, filename), image)
