import cloudinary


def default_pic_details():
    return cloudinary.utils.cloudinary_url('profiles/default.png')[0]


def upload_picture(picture, *, picture_public_id='profiles/'):
    '''Upload picture to cloudinary'''
    return cloudinary.uploader.upload(
        picture,
        public_id=picture_public_id
    )
