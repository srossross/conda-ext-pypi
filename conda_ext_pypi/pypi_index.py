from conda_install2.index import Index
import requests as req
from conda_install2.package import Package
from conda_install2.utils import make_safe_version
from semantic_version import Version
from binstar_client.inspect_package import pypi as pypi_inspect
CHUNK_SIZE = 2 ** 15


class PyPI(Index):
    """
    This index should fetch the data from a pypi json repo
    """

    def __init__(self, env, uri=None, user_channels=()):
        self.uri = uri
        self.user_channels = user_channels
        Index.__init__(self, env)

    def get_package(self, spec, parent_channels=()):

        res = req.get('https://pypi.python.org/pypi/%s/json' % spec.package)
        info = res.json()
        versions = {Version.coerce(v):r for v, r in info['releases'].items()}
        version = max(spec.version_spec.filter(versions.keys()))
        releases = versions[version]

        data = info['info']
        data['files'] = []

        for file_info in releases:
            file_info['basename'] = file_info['filename']
            file_info['attrs'] = {'packagetype': file_info['packagetype']}
            file_info['distribution_type'] = 'pypi'
            file_info['version'] = str(version)
            file_info['md5'] = file_info['md5_digest']

            data['files'].append(file_info)

        pkg = Package(self.env, data)

        self.fetch(pkg.file)

        with open(pkg.file.cache_path) as fileobj:
            _, _, data = pypi_inspect.inspect_pypi_package(pkg.file.cache_path, fileobj)
            file_info['dependencies'] = data.get('dependencies', [])

        return pkg

    def fetch(self, package_file):

        if not package_file.cached:
            print("fetch", package_file.cache_path)
            url = package_file.data['url']
            res = req.get(url, stream=True)

            with open(package_file.cache_path, 'wb') as to_file:
                data = res.raw.read(CHUNK_SIZE)
                while data:
                    to_file.write(data)
                    data = res.raw.read(CHUNK_SIZE)

