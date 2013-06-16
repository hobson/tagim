# setup.py for Tagim
from distutils.core import setup
import os
from tagim import __version__

setup(
    name="tagim",
    # packages=["tg"],
    version=__version__,
    description="Image EXIF tagging from the command line.",
    long_description=open(os.path.realpath(os.path.join(os.path.dirname(__file__)), 'README.md')).read(),
    author="Hobson Lane",
    author_email="hobson@totalgood.com",
    url="http://github.com/hobsonlane/tagim/",
    # download_url="https://github.com/hobsonlane/tagim/archive/v%s.tar.gz" % VERSION,
    keywords=["bitcoin", "agent", "bot", "ai", "finance", "trend", "trade"],
    classifiers=[
                    "Programming Language :: Python",
                    "Development Status :: 2 - Pre-Alpha",
                    "Environment :: Other Environment",
                    # "Environment :: Console",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
                    "Operating System :: OS Independent",
                ],
)
