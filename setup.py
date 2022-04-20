import setuptools

setuptools.setup(
    name="sun_calculator",
    version="0.0.2",
    author="Seojin Kim",
    author_email="sjkim@conalog.com",
    description="Sun Calculator for Digital Twin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        "numpy"
    ]
)
