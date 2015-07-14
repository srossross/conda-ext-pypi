from conda_install2.file_type.base import File
from subprocess import Popen, STDOUT, PIPE
import os
from conda_install2.package_spec import PackageSpec
from conda_install2.errors import InstallError

class PyPIFile(File):
    """
    Install a pypi dist or bdist_wheel
    """
    PRIORITY = 5

    @property
    def installed(self):
        return self.env.has_info_file(self.package, self.version)

    def install(self):
        #
        exe = os.path.join(self.env.prefix, 'bin', 'pip')
        p0 = Popen([exe, '--isolated', 'install', self.cache_path, '--no-deps'], stderr=STDOUT, stdout=PIPE)

        exitcode = p0.wait()

        if exitcode != 0:
            output = "Running: %s" % ' '.join([exe, 'install', self.cache_path, '--no-deps'])
            output = p0.stdout.read()
            raise InstallError("Error installing %s" % self.basename, output)
            print('')

        info = dict(self.data)
        info['name'] = self.package

        self.env.add_info_file(self.package, self.version, info)

        return

    @property
    def depends(self):
        if self._depends is None:
            dependencies = self.data.get('dependencies') or {}
            depends = dependencies.get('depends') or []
            self._depends = [PackageSpec(d['name'], operators=d.get('specs') or []) for d in depends]

            # Add pip as a dependency
            self._depends.append(PackageSpec('pip'))

        return self._depends

    PKG_TYPE_PRIORITIES = {'bdist_wheel':2, 'sdist': 1}

    def __lt__(self, other):
        """
        prioritize bdist_wheel > sdist > other packages that are otherwise the same
        """

        if File.__lt__(self, other):
            return True

        P = self.PKG_TYPE_PRIORITIES.get

        tself = P(self.data['attrs'].get('packagetype'), 0)
        tother = P(other.data['attrs'].get('packagetype'), 0)

        return tself < tother


