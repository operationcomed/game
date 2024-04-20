from setuptools import setup

# to build (must be in the directory where this file is located):
# python setup.py build_apps
# to build and zip:
# python setup.py bdist_apps

# https://docs.panda3d.org/1.10/python/distribution/building-binaries
setup(
    name='escapemsu',
	version='0.0.2',
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
                'icon.ico',
                'assets/**',
                'maps/random.rgb', # i have no idea why this file is needed :(
            ],

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
				'p3ffmpeg',
            ],
			
			"icons": {
			    # The key needs to match the key used in gui_apps/console_apps.
			    # Alternatively, use "*" to set the icon for all apps.
			    "escapemsu": ["assets/media/icon.png"],
			},
			"bam_model_extensions": {
				".glb"
            },
			"include_modules": {
				"escapemsu": ["direct.particles", "direct.showbase.PhysicsManagerGlobal"],
            },
        }
    }
)