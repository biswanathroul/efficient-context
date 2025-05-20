from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="efficient-context",
    version="0.1.0",
    author="Biswanath Roul",
    description="Optimize LLM context handling in CPU-constrained environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biswanathroul/efficient-context",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scikit-learn>=0.24.0",
        "sentence-transformers>=2.2.2",
        "nltk>=3.6.0",
        "pydantic>=1.8.0",
        "tqdm>=4.62.0",
    ],
    keywords="llm, context, optimization, cpu, memory, efficiency, nlp",
)