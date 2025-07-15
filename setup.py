from setuptools import setup, find_packages

setup(
    name="flexistore",
    version="0.1.0",
    description="Cloud-agnostic storage interface and Azure Blob implementation with CLI",
    author="Your Name",
    packages=find_packages(where=".", include=["flexistore", "flexistore.*"]),
    install_requires=[
        "azure-storage-blob>=12.0.0",
        "python-dotenv>=0.15.0"
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'flexistore-cli = flexistore.cli:main'
        ]
    }
)