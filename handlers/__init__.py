from .common_handlers import register_handlers as register_common
from .phoun_handlers import register_handlers as register_phoun
from .ai_handlers import register_handlers as register_ai
from .image_handlers import register_handlers as register_image
from .code_handlers import register_handlers as register_code
from .photo_handlers import register_handlers as register_photo

__all__ = ['register_common', 'register_phoun', 'register_ai', 'register_image', 'register_code', 'register_photo']
