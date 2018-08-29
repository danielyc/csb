import urllib.request, urllib.error, os.path


class updateManager():
    def __init__(self, url, version, filename='VERSION', debug=False):
        self.url = url.replace('github', 'raw.githubusercontent') + '/master/' + filename
        self.version = version
        self.filename = filename
        self.create_version_file()
        self.update_local_file()
        if self.check_for_update(self.check_remote_version(), self.check_local_version()):
            if debug: print('UPDATE FOUND')
            self.update = True
        else:
            self.update = False

    @staticmethod
    def check_for_update(remote, local):
        remote = remote.split('.')
        local = local.split('.')
        if len(remote) > len(local):
            for x in range(len(local)):
                if int(remote[x]) < int(local[x]):
                    return False
            return True
        elif len(remote) <= len(local):
            for x in range(len(remote)):
                if int(remote[x]) < int(local[x]):
                    return False
            return True

    def create_version_file(self):
        if not os.path.isfile(self.filename):
            open(self.filename, 'w').write(self.version)

    def update_local_file(self):
        if self.check_for_update(self.version, self.check_local_version()):
            open(self.filename, 'w').write(self.version)
        elif self.check_for_update(self.check_local_version(), self.version):
            print('ERROR: VERSION file higher than script version')

    def check_remote_version(self):
        try:
            req = urllib.request.urlopen(self.url)
            return req.read().decode()[:-1]
        except urllib.error.HTTPError:
            print('ERROR: remote VERSION file not accessible')
            exit(1)

    def check_local_version(self):
        if not os.path.isfile(self.filename):
            print('Local version file not found')
            return None
        return open(self.filename, 'r').read()