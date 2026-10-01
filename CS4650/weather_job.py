# mrjob 0.7.4 imports the removed Python 3.13+ 'pipes' module.
# This tiny compatibility shim keeps the assignment runnable on Python 3.14.
import shlex, shutil, sys, types
from packaging.version import Version
sys.modules.setdefault('pipes', types.SimpleNamespace(quote=shlex.quote))
distutils = types.ModuleType('distutils')
distutils_spawn = types.ModuleType('distutils.spawn')
distutils_spawn.find_executable = shutil.which
distutils.spawn = distutils_spawn
distutils_version = types.ModuleType('distutils.version')
distutils_version.LooseVersion = Version
distutils.version = distutils_version
sys.modules.setdefault('distutils', distutils)
sys.modules.setdefault('distutils.spawn', distutils_spawn)
sys.modules.setdefault('distutils.version', distutils_version)

from mrjob.job import MRJob
from mrjob.protocol import RawValueProtocol

# The accepted quality codes specified in the assignment.
VALID_QUALITY = {'0', '1', '4', '5', '9'}

class WindDirectionTemperature(MRJob):
    INPUT_PROTOCOL = RawValueProtocol

    def mapper(self, _, line):
        if len(line) < 93:
            return

        wind_direction = line[60:63]
        wind_quality = line[63:64]
        temperature_text = line[87:92]
        temperature_quality = line[92:93]

        if (wind_direction == '999' or
                wind_quality not in VALID_QUALITY or
                temperature_text in {'+9999', '-9999'} or
                temperature_quality not in VALID_QUALITY):
            return

        yield int(wind_direction), {
            'low': int(temperature_text),
            'high': int(temperature_text),
            'count': 1
        }

    def reducer(self, wind_direction, records):
        low = None
        high = None
        count = 0

        for record in records:
            low = record['low'] if low is None else min(low, record['low'])
            high = record['high'] if high is None else max(high, record['high'])
            count += record['count']

        yield wind_direction, {'low': low, 'high': high, 'count': count}
