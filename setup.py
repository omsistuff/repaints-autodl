from cx_Freeze import setup, Executable

executables = [Executable("main.py", base = "Win32GUI")]

options = {
    'build_exe': {    
        'packages': ['requests', 'hashlib', 'os', 'webbrowser', 'websockets',
            'asyncio', 'time', 'sys', 'zipfile'],
    },
}

setup(
    name = "OmsiStuff - Installation automatique",
    options = options,
    version = "1.0",
    description = 'Installe automatiquement des repaints pour OMSI 2 depuis la page web omsistuff.fr',
    executables = executables
)