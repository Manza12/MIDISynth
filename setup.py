from distutils.core import setup

setup(
    name="MIDISynth",
    packages=['MIDISynth'],
    version="0.0.11",
    license='MIT',
    description="A package for synthesizing audio from MIDI.",
    author="Gonzalo Romero-García",
    author_email="tritery@hotmail.com",
    url="https://github.com/Manza12/MIDISynth",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    python_requires=">=3.6",
)
