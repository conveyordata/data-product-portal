"""Setup configuration for S3 Data Output Plugin"""

from setuptools import find_packages, setup

setup(
    name="data-product-portal-s3-plugin",
    version="1.0.0",
    description="S3 data output configuration plugin for Data Product Portal",
    author="Data Product Portal Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
    ],
    entry_points={
        "data_product_portal.plugins": [
            "S3DataOutput = s3_plugin.schema:S3DataOutput",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
