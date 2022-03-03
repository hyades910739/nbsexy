import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="nbsexy",
    version="0.0.1",
    author="hyades910739",
    author_email="hyades910739@gmail.com",
    description="A tool to make your notebook sexier than before.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyades910739/nbsexy",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "nbsexy = nbsexy.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["colorama>=0.4.4"],
)
