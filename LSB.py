from utils import *


class LSB:
    def __init__(self):
        print('LSB class has been initialized')

    @staticmethod
    def __prepare_hide(input_image: str, input_file: str) -> tuple[Image, BinaryIO]:
        try:
            image = Image.open(input_image)
            file = open(input_file, 'rb')
        except Exception:
            raise ValueError('[PREPARE HIDE]: Input image/file could not open')
        return image, file

    @staticmethod
    def __hide_message_in_image(input_image: Image, input_file: BinaryIO, lsb_number: int):
        try:
            message = input_file.read()
            input_file.close()
        except Exception:
            raise ValueError('[HIDE MESSAGE IN IMAGE]: Message could not be read')

        image = input_image
        number_of_channels = len(image.getdata()[0])
        print(f'Number of image channels: {number_of_channels}')

        flattened_color_data = [v for t in image.getdata() for v in t]

        message_size = len(message)
        file_size_tag = message_size.to_bytes(
            bytes_in_max_file_size(image, lsb_number), byteorder=sys.byteorder
        )
        data = file_size_tag + str_to_bytes(message)

        if 8 * len(data) > max_bits_to_hide(image, lsb_number):
            return(
                f"Only able to hide {max_bits_to_hide(image, lsb_number) // 8} bytes "
                + f"in this image with {lsb_number} LSBs, but {len(data)} bytes were requested"
            )

        flattened_color_data = lsb_interleave_list(flattened_color_data, data, lsb_number)

        image.putdata(list(zip(*[iter(flattened_color_data)] * number_of_channels)))
        return image

    def hide_data(self, input_image: str, input_file: str, output_image: str, lsb_number: int) -> Union[None, str]:
        if input_image is None:
            raise ValueError('[HIDE DATA]: Input image not found')
        if input_file is None:
            raise ValueError('[HIDE DATA]: Input file not found')
        if output_image is None:
            raise ValueError('[HIDE DATA]: Output file not found')

        image, file = self.__prepare_hide(input_image, input_file)
        image = self.__hide_message_in_image(image, file, lsb_number)
        if isinstance(image, str):
            return image
        else:
            image.save(output_image)

    @staticmethod
    def __prepare_recover(input_image: str, output_file: str) -> tuple[Image, BinaryIO]:
        try:
            image = Image.open(input_image)
            file = open(output_file, 'wb+')
        except Exception:
            raise ValueError('[PREPARE RECOVER]: Input image/file could not open')
        return image, file

    @staticmethod
    def __recover_message_from_image(input_image: Image, lsb_number: int) -> Union[str, bytes]:
        image = input_image

        color_data = [v for t in image.getdata() for v in t]

        file_size_tag_size = bytes_in_max_file_size(image, lsb_number)
        tag_bit_height = roundup(8 * file_size_tag_size / lsb_number)

        bytes_to_recover = int.from_bytes(
            lsb_deinterleave_list(
                color_data[:tag_bit_height], 8 * file_size_tag_size, lsb_number
            ),
            byteorder=sys.byteorder,
        )

        maximum_bytes_in_image = (
                max_bits_to_hide(image, lsb_number) // 8 - file_size_tag_size
        )
        if bytes_to_recover > maximum_bytes_in_image:
            return(
                "This image appears to be corrupted.\n"
                + f"It claims to hold {bytes_to_recover} B, "
                + f"but can only hold {maximum_bytes_in_image} B with {lsb_number} LSBs"
            )

        data = lsb_deinterleave_list(
            color_data, 8 * (bytes_to_recover + file_size_tag_size), lsb_number
        )[file_size_tag_size:]

        return data

    def recover_data(self, input_image: str, output_file: str, lsb_number: int) -> Union[str, bytes]:
        if input_image is None:
            raise ValueError('[RECOVER DATA]: Input image not found')
        if output_file is None:
            raise ValueError('[RECOVER DATA]: Output file not found')

        image, file = self.__prepare_recover(input_image, output_file)
        data = self.__recover_message_from_image(image, lsb_number)
        if isinstance(data, str):
            return data
        else:
            file.write(data)
            file.close()
            return data
