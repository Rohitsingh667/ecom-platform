from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "recommendations.fast_similarity",
        ["recommendations/fast_similarity.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
    ),
    Extension(
        "recommendations.matrix_operations",
        ["recommendations/matrix_operations.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
    ),
]

setup(
    name="ecommerce_recommendations",
    ext_modules=cythonize(extensions),
    zip_safe=False,
)
