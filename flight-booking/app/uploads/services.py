import cloudinary


def UNSAFE_default_pic_details():
    return cloudinary.utils.cloudinary_url('profiles/default.png')[0]
