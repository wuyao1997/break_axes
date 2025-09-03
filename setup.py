import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="break_axes",
    version="0.2.0",
    author="Wu Yao",
    author_email="wuyao@qq.com",
    description="A Matplotlib-based utility module for creating broken axes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wuyao1997/break_axes",
    py_modules=["break_axes"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
