import argparse

from Converter import Converter
from Explorer import Explorer


def main():
    parser = argparse.ArgumentParser(
        description='Creates a classification dataset from a segmentation one.'
    )
    parser.add_argument(
        'path',
        type=str,
        help='Absolute path containing the images and masks folders.')
    parser.add_argument('--patch_size',
                        type=int,
                        default=224,
                        help='Size of each patch.')
    parser.add_argument('--max_patches_per_image',
                        type=int,
                        default=100,
                        help='How many patches to extract from each image.')
    args = parser.parse_args()

    explorer = Explorer(args.path)
    converter = Converter(explorer,
                          patch_size=args.patch_size,
                          max_patches_per_image=args.max_patches_per_image)
    converter.process_images()


if __name__ == '__main__':
    main()
