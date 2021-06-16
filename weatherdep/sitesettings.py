from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'weatherdep',
        'USER': 'postgres',
        'PASSWORD': 'maciej',
        'HOST': 'localhost',
        'PORT': '5432',
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
	}
}

OPENWEATHER_KEY = '33d8760e822fee77037e59ec42a25fd1'
