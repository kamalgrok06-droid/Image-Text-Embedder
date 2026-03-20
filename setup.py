from setuptools import setup, find_packages

setup(
    name="image-text-embedder",
    version="1.0.0",
    author="Image Text Embedder",
    description="Batch embed customizable text overlays on images",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["Pillow>=10.0.0"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "image-text-embedder=ImageTextEmbedder:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/kamalgrok06/Image-Text-Embedder",
)
