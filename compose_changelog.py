from debian.changelog import Changelog, Version

changelog = Changelog()

changelog.new_block(package='python-tagim',  # will likely need a tagim package that depends on this library
                    version=Version('0.1'),
                    distributions='unstable',
                    urgency='low',
                    author='Hobson Lane <hobsonlane@gmail.com>', # name and e-mail must match your GPG key
                    date='Thu, 26 Jan 2012 08:29:40 +1100', # must be in the format of `date -R`
                    )

changelog.add_change('');
changelog.add_change('  * Welcome to tagim');
changelog.add_change('  * Features');
changelog.add_change('    - tag images with text embedded in EXIF comment field');
changelog.add_change('    - chose random image from selected folder or tree of folders and display on desktop background at prescribed intervals');
changelog.add_change('');

print changelog

