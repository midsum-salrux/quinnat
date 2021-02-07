import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quinnat",
    version="1.0.0",
    author="~midsum-salrux",
    author_email="",
    description="Library for building chatbots on urbit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=['urlock'],
    classifiers=[],
    python_requires='>=3.9',
)
