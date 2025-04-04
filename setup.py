from setuptools import setup, find_packages

setup(
    name="2print",
    version="0.1.22",
    description="Print from html to pdf, zpl, image, printer: html to print, html2print, html to pdf,html2pdf, pdf to print, pdf2print, zpl to print,zpl2print, image to print,  image2print, ",
    author="Tom Softreck",
    author_email="info@softreck.dev",
    url="https://github.com/2print/2print",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
