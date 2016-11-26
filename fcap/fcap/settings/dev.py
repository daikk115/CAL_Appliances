from base import *

# #########################################################

# ##### DEBUG CONFIGURATION ###############################
DEBUG = True


# ##### APPLICATION CONFIGURATION #########################

INSTALLED_APPS = DEFAULT_APPS

INSTALLED_APPS.extend([
    'authentication',
    'management',
])