import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    'handlers': {
    'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'elasticapm': {
            'level': 'WARNING',
            'class': 'elasticapm.contrib.django.handlers.LoggingHandler',
        },

    },
    "formatters": {
        "verbose": {
             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'inventario': {
            'level': 'WARNING',
            'handlers': ['elasticapm'],
            'propagate': False,
        },
        # Log errors from the Elastic APM module to the console (recommended)
        'elasticapm.errors': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}