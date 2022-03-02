# import os.path
# from os import walk
# from typing import Optional
# from wand.image import Image


# def crop_image(
#     filename: str,
#     new_filename: str,
#     scale: Optional[int] = 0,
#     crop_no: Optional[int] = 0,
# ):
#     img = Image(filename=filename)

#     old_height, old_width = img.height, img.width
#     size = min(old_width, old_height) * 80 // 100

#     crops = [
#         {"top": 0, "left": 0, "width": size, "height": size},
#         {"top": 0, "left": old_width - size, "width": size, "height": size},
#         {"top": old_height - size, "left": 0, "width": size, "height": size},
#         {
#             "top": old_height - size,
#             "left": old_width - size,
#             "width": size,
#             "height": size,
#         },
#     ]

#     img.crop(**crops[crop_no])
#     img.resize(width=500, height=500)

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
#                 filepath_without_ext = filepath[: -len(ext) - 1]
#                 new_ext = "png" if ext == "png" else "jpg"

#                 for crop in range(4):
#                     new_filepath = (
#                         f"{filepath_without_ext}-{crop}.{ext}.500x500.{new_ext}"
#                     )
#                     if os.path.isfile(new_filepath):
#                         print(f"exist {new_filepath}")
#                         continue

#                     crop_image(
#                         filename=filepath,
#                         new_filename=new_filepath,
#                         scale=80,
#                         crop_no=crop,
#                     )
#                     print(f"crop {fn}", crop)
#             else:
#                 print(f"skip {fn}")
