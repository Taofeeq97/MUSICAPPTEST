import os
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image


class ProfilePictureValidator:
    """
    Validates profile pictures based on settings configuration
    """
    
    @staticmethod
    def validate_extension(value):
        ext = os.path.splitext(value.name)[1][1:].lower()
        allowed_extensions = settings.PROFILE_PICTURE_SETTINGS['ALLOWED_EXTENSIONS']
        
        if ext not in allowed_extensions:
            raise ValidationError(
                f'Unsupported file extension. Allowed extensions: {", ".join(allowed_extensions)}'
            )
    
    @staticmethod
    def validate_file_size(value):
        max_size = settings.PROFILE_PICTURE_SETTINGS['MAX_FILE_SIZE']
        
        if value.size > max_size:
            raise ValidationError(
                f'File size too large. Max size is {max_size/1024/1024}MB'
            )
    
    @staticmethod
    def validate_dimensions(value):
        min_width, min_height = settings.PROFILE_PICTURE_SETTINGS['MIN_DIMENSIONS']
        
        try:
            image = Image.open(value)
            width, height = image.size
            
            if width < min_width or height < min_height:
                raise ValidationError(
                    f'Image dimensions too small. Minimum size is {min_width}x{min_height} pixels'
                )
                
        except Exception as e:
            raise ValidationError('Unable to read image file') from e
    
    @classmethod
    def validate_all(cls, value):
        cls.validate_extension(value)
        cls.validate_file_size(value)
        cls.validate_dimensions(value)