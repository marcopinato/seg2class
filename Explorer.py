import glob
import os
import pathlib
from typing import Iterable, List, Tuple


class Explorer:
    def __init__(self, master_path: str):
        self.master_path = master_path
        # Images and masks folders paths
        self.folders = self._get_data_folders(self.master_path)
        # List of classes
        self.images_classes_paths = self.get_classes_paths(self.folders[0])
        self.masks_classes_paths = self.get_classes_paths(self.folders[1])

    def _get_data_folders(self, master_path: str) -> List[str]:
        """
        Returns a list containing images and masks folder names.
        """
        subfolders = [f.path for f in os.scandir(master_path) if f.is_dir()]
        try:
            images = self._extract_folder('images', subfolders)
            masks = self._extract_folder('masks', subfolders)
            return [images, masks]
        except ValueError:
            raise ValueError(
                'Unable to find images and masks subfolders in %s' %
                master_path)

    def _extract_folder(self, folder: str, folders: List[str]) -> str:
        """
        Returns a folder from a list of folders, according to a specified criterion.
        """
        for f in folders:
            if folder in f.lower():
                return f
        raise ValueError('Invalid folder.')

    def _get_filenames(self, folder: str,
                       only_images: bool = True) -> List[str]:
        """
        Returns a list of filenames in a given folder. Defaults to returning
        only images.
        """
        filenames = [
            file for file in glob.glob(folder + '**/*.*', recursive=True)
            if self._is_image(file)
        ] if only_images else glob.glob(folder + '**/*.*', recursive=True)

        return filenames

    def _is_image(self, filename: str) -> bool:
        """
        Returns True if @filename is an image file, based on its extension.
        """
        extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif']
        checks = [
            True if filename.lower().endswith(extension) else False
            for extension in extensions
        ]

        return True in checks

    def yield_image_mask_filename_pair(self, images_folder: str,
                                       masks_folder) -> Iterable:
        """
        Yields the corresponding pair of image and mask.
        """
        images = self._get_filenames(images_folder)
        masks = self._get_filenames(masks_folder)

        for pair in zip(images, masks):
            yield pair

    def get_classes_paths(self, folder: str) -> List[str]:
        """
        Returns a list of subfolders. 
        """
        return [
            subfolder
            for subfolder in glob.glob(folder + '**/*', recursive=False)
        ]

    def get_output_path_for_class(self, paths: List[str],
                                  class_name: str) -> str:
        """
        Returns the corresponding path from @paths for the class with name 
        @class_name.
        """
        try:
            return next(
                path for path in paths
                if self.extract_class_name(path).lower() == class_name.lower())
        except StopIteration:
            raise ValueError('Class not found.')

    def get_images_and_masks_paths(self) -> List[Tuple[str, str]]:
        """
        Zips together the corresponding images and masks folders.
        """
        return list(zip(self.images_classes_paths, self.masks_classes_paths))

    def extract_class_name(self, folder_path: str) -> str:
        """
        Extracts the last portion of a @folder_path name, representing the class 
        name.
        """
        return os.path.basename(folder_path)

    def get_classes_names(self) -> List[str]:
        """
        Returns the list of images (equal to masks) class names.
        """
        return [
            self.extract_class_name(folder)
            for folder in self.images_classes_paths
        ]

    def _get_output_master_path(self) -> str:
        """
        Returns the output master path, inside which the background and 
        foreground folders will be created.  
        """
        return os.path.join(self.master_path, 'output')

    def create_output_folders(self) -> None:
        """
        Creates output folders.
        """
        output_path = self._get_output_master_path()
        class_names = self.get_classes_names()

        # Background is common to all classes, while foreground is different
        # for each class
        foreground_path = os.path.join(output_path, 'foreground')
        self.image_classes_paths = [
            os.path.join(foreground_path, class_name)
            for class_name in class_names
        ]
        self.background_path = os.path.join(output_path, 'background')

        for path in [foreground_path, self.background_path]:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        for path in self.image_classes_paths:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
