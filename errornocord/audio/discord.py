import audioop

import disnake


class TrackedAudioSource(disnake.AudioSource):
    def __init__(self, source):
        self._source = source
        self.read_count = 0

    def read(self) -> bytes:
        data = self._source.read()
        if data:
            self.read_count += 1
        return data

    def fast_forward(self, seconds: int):
        for _ in range(int(seconds / 0.02)):
            self.read()

    @property
    def progress(self) -> float:
        return self.read_count * 0.02


class PCMVolumeTransformer(disnake.AudioSource):
    def __init__(self, original: TrackedAudioSource, volume: float = 1.0) -> None:
        if original.is_opus():
            raise disnake.ClientException("AudioSource must not be Opus encoded")

        self.original = original
        self.volume = volume

    def cleanup(self) -> None:
        self.original.cleanup()

    def read(self) -> bytes:
        ret = self.original.read()
        return audioop.mul(ret, 2, self.volume)
