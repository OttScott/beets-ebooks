from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="beets-ebooks",
    version="0.1.0",
    author="Scott Ott",
    author_email="ottscott@gmail.com",
    description="A Beets plugin for managing ebook collections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OttScott/beets-ebooks",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beets>=1.6.0",
        "requests>=2.25.0",
        "ebooklib>=0.18",
    ],
    extras_require={
        "pdf": ["PyPDF2>=3.0.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "flake8",
            "black",
        ],
    },
    entry_points={
        "beets.plugins": [
            "ebooks = beetsplug.ebooks:EBooksPlugin",
        ],
    },
)
