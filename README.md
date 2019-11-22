# seg2class

_seg2class_ is a simple Python library to create a classification dataset starting from a segmentation one.
This is achieved by extracting corresponding patches from the images and the masks in the segmentation dataset and subsequently classifying each patch based on the mask content.

_seg2class_ automatically detects the mask type (whether active pixels are white or black) and creates an output folder structure to reflect the dataset composition.

You can learn more about this project by visiting seg2class.github.io

## Setup

### Get the code

You can clone _seg2class_ using https:

`git clone https://github.com/marcopinato/seg2class.git`

or, if you already have a GitHub account set up with an SSH key, using SSH:

`git clone git@github.com:marcopinato/seg2class.git`

After cloning the repository, access the folder before moving forward with the next steps:

`cd seg2class`

### Install dependencies

If you're on Windows, you should probably use the `pip` and `python` commands instead of `pip3` and `python3`.

Install dependencies with:

`pip3 install -r requirements.txt`

## Expected folder structure

_seg2class_ expects the dataset to be organized in a standard way:

```
├── dataset
    ├── images
    |   ├── class1
    |   |   ├── filename1.jpg
    |   |   ├── filename2.jpg
    |   |   └── ...
    |   ├── class2
    |   └── ...
    ├── masks
        ├── class1
        |   ├── filename1.jpg
        |   ├── filename2.jpg
        |   └── ...
        ├── class2
        └── ...
```

Corresponding images and masks must have the same name.

## Launch seg2class

The main file used to start the conversion is called `seg2class.py`. It expects at least one argument - the dataset's absolute path.

Using the `-h` argument you can obtain a list of the additional available options:

- _patch_size_ : size of the (squared) patch to extract (defaults to 224 px).
- _max_patches_per_image_ : maximum number of patches to extract from each image (defaults to 100).

```
$ python3 seg2class.py -h
usage: seg2class.py [-h] [--patch_size PATCH_SIZE]
                       [--max_patches_per_image MAX_PATCHES_PER_IMAGE]
                       path

Creates a classification dataset from a segmentation one.

positional arguments:
  path                  Absolute path containing the images and masks folders.

optional arguments:
  -h, --help            show this help message and exit
  --patch_size PATCH_SIZE
                        Size of each patch.
  --max_patches_per_image MAX_PATCHES_PER_IMAGE
                        How many patches to extract from each image.
```

### Example

To generate a classification dataset comprised of patches with dimension _126_ x _126_ px, starting from images and masks contained inside folders in _/home/marco/dataset_ and extracting a maximum of _10_ patches for each image, use the command:

`python3 seg2class.py /home/marco/dataset --patch_size=126 --max_patches_per_image=10`

## Output

_seg2class_ creates an `output` folder inside the main dataset folder. This contains a `foreground` and `background` folder:

```
├── dataset
    ├── images
    ├── masks
    ├── output
        ├── foreground
        |   ├── class1
        |   |   ├── fg_patch1.jpg
        |   |   ├── fg_patch2.jpg
        |   |   └── ...
        |   ├── class2
        |   └── ...
        ├── background
            ├── bg_patch1.jpg
            ├── bg_patch2.jpg
            └── ...
```

The foreground is comprised by patches having more than a set percentage of their pixels marked as active in the corresponding masks. The background is assumed to be common to all images, so background patches are all placed in the same folder regardless of their original class.

## License

_seg2class_ is released under the MIT license.
