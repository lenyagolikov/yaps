# import os.path
# from os import walk
# from typing import Optional
# from wand.image import Image


# def resize_image(
#     filename: str,
#     new_width: int,
#     new_height: int,
#     postfix: str,
#     scale: Optional[int] = None,
# ):
#     new_filename = filename + postfix
#     if os.path.isfile(new_filename):
#         return False

#     img = Image(filename=filename)

#     old_height, old_width = img.height, img.width
#     if old_width * new_height > old_height * new_width:
#         new_height = new_width * old_height // old_width
#     else:
#         new_width = new_height * old_width // old_height

#     if new_width < old_width and new_height < old_height:
#         img.resize(new_width, new_height)
#     if scale:
#         img.compression_quality = scale

#     img.save(filename=new_filename)
#     return True


# if __name__ == "__main__":
#     path = "/media/media/iblock"
#     # path = '/home/damir/web/yaps' + path
#     for dirpath, _, filenames in walk(
#         path, topdown=True, onerror=None, followlinks=False
#     ):
#         for fn in filenames:
#             *_, prefix, ext = fn.lower().split(".")
#             if prefix not in {"100x100", "500x500"} and ext in {
#                 "png",
#                 "jpg",
#                 "jpeg",
#                 "gif",
#                 "JPEG",
#                 "bmp",
#                 "JPG",
#             }:
#                 filepath = dirpath + "/" + fn
#                 file_postfix = ".500x500." + ("png" if ext == "png" else "jpg")
#                 ans = resize_image(
#                     filename=filepath,
#                     new_width=500,
#                     new_height=500,
#                     postfix=file_postfix,
#                     scale=80,
#                 )

#                 if ans:
#                     print(f"resize {fn}")
#                 else:
#                     print(f"exist {fn}{file_postfix}")

#                 # resize_image(
#                 #     filename=filepath,
#                 #     new_width=100,
#                 #     new_height=100,
#                 #     postfix='.100x100.png',
#                 # )
#             else:
#                 print(f"skip {fn}")
