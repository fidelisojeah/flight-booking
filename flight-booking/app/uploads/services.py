import cloudinary


def default_pic_details():
    return cloudinary.utils.cloudinary_url('profiles/default.png')[0]
