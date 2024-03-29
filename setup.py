from setuptools import setup

# https://docs.panda3d.org/1.10/python/distribution/building-binaries
setup(
    name='escapemsu',
    options={
        'build_apps': {
			'platforms': ['win_amd64'],
            # Build asteroids.exe as a GUI application
            'gui_apps': {
                'escapemsu': 'main.py',
            },

            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/OperationComEd/EscapeMSU/output.log',
            'log_append': False,

            # Specify which files are included with the distribution
            'include_patterns': [
                '*.ico',
                '**/*.png',
                '**/*.jpg',
                '**/*.avi',
                '**/*.mp3',
                '**/*.wav',
                '**/*.glb',
                'ROT_SCENE',
            ],

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
			
			"icons": {
			    # The key needs to match the key used in gui_apps/console_apps.
			    # Alternatively, use "*" to set the icon for all apps.
			    "escapemsu": ["icon.png"],
			},
        }
    }
)