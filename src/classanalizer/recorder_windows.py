"""Captura de audio para Windows mediante WASAPI Loopback."""

import argparse
import subprocess
import wave
from pathlib import Path

from classanalizer.platform_utils import get_ffmpeg_binary


OUTPUT_SAMPLE_RATE = 44_100
FRAMES_PER_BUFFER = 1_024


def _to_mono(samples, channels: int, numpy):
    """Convierte un buffer PCM intercalado a una señal mono normalizada."""
    if not samples.size:
        return numpy.empty(0, dtype=numpy.float32)
    frames = samples.reshape(-1, channels).astype(numpy.float32)
    return frames.mean(axis=1) / 32_768.0


def _resample(samples, source_rate: int, target_rate: int, numpy):
    """Remuestrea linealmente un buffer corto sin añadir otra dependencia."""
    if not samples.size or source_rate == target_rate:
        return samples
    target_length = max(1, round(len(samples) * target_rate / source_rate))
    old_positions = numpy.linspace(0.0, 1.0, num=len(samples))
    new_positions = numpy.linspace(0.0, 1.0, num=target_length)
    return numpy.interp(new_positions, old_positions, samples).astype(numpy.float32)


def _read_mono(stream, channels: int, sample_rate: int, numpy):
    raw = stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
    samples = numpy.frombuffer(raw, dtype=numpy.int16)
    return _resample(_to_mono(samples, channels, numpy), sample_rate, OUTPUT_SAMPLE_RATE, numpy)


def _find_loopback_device(audio, default_speakers):
    speaker_name = str(default_speakers.get("name", ""))
    for device in audio.get_loopback_device_info_generator():
        if speaker_name and speaker_name in str(device.get("name", "")):
            return device
    return None


def _open_input_stream(audio, pyaudio, device_info):
    channels = min(2, int(device_info.get("maxInputChannels", 0)))
    if channels < 1:
        raise RuntimeError(f"El dispositivo no tiene canales de entrada: {device_info.get('name')}")
    sample_rate = int(float(device_info.get("defaultSampleRate", OUTPUT_SAMPLE_RATE)))
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        input_device_index=int(device_info["index"]),
        frames_per_buffer=FRAMES_PER_BUFFER,
    )
    return stream, channels, sample_rate


def record_wasapi_process(output_mp3: Path, source: str, stop_file: Path) -> None:
    """Graba hasta que exista ``stop_file`` y genera el MP3 final."""
    import numpy as np
    import pyaudiowpatch as pyaudio

    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    temp_wav = output_mp3.with_suffix(".temp.wav")
    audio = pyaudio.PyAudio()
    streams = []
    wave_file = None
    wrote_frames = False

    try:
        wasapi_info = audio.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = audio.get_device_info_by_index(
            int(wasapi_info["defaultOutputDevice"])
        )
        default_mic = audio.get_device_info_by_index(
            int(wasapi_info["defaultInputDevice"])
        )

        loopback_info = (
            default_speakers
            if default_speakers.get("isLoopbackDevice")
            else _find_loopback_device(audio, default_speakers)
        )
        if source in ("meet", "both") and loopback_info is None:
            raise RuntimeError(
                "No se encontró el dispositivo WASAPI Loopback de la salida predeterminada."
            )

        loop_stream = mic_stream = None
        loop_channels = mic_channels = 0
        loop_rate = mic_rate = OUTPUT_SAMPLE_RATE

        if source in ("meet", "both"):
            loop_stream, loop_channels, loop_rate = _open_input_stream(
                audio, pyaudio, loopback_info
            )
            streams.append(loop_stream)
        if source in ("mic", "both"):
            if int(default_mic.get("maxInputChannels", 0)) < 1:
                raise RuntimeError("No se encontró un micrófono WASAPI con entrada disponible.")
            mic_stream, mic_channels, mic_rate = _open_input_stream(
                audio, pyaudio, default_mic
            )
            streams.append(mic_stream)

        wave_file = wave.open(str(temp_wav), "wb")
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(OUTPUT_SAMPLE_RATE)

        while not stop_file.exists():
            loop_data = (
                _read_mono(loop_stream, loop_channels, loop_rate, np)
                if loop_stream
                else None
            )
            mic_data = (
                _read_mono(mic_stream, mic_channels, mic_rate, np)
                if mic_stream
                else None
            )

            if loop_data is not None and mic_data is not None:
                length = max(len(loop_data), len(mic_data))
                mixed = np.zeros(length, dtype=np.float32)
                mixed[: len(loop_data)] += loop_data * 0.5
                mixed[: len(mic_data)] += mic_data * 0.5
            else:
                mixed = loop_data if loop_data is not None else mic_data

            if mixed is not None and len(mixed):
                pcm = np.clip(mixed, -1.0, 1.0)
                wave_file.writeframes((pcm * 32_767).astype(np.int16).tobytes())
                wrote_frames = True
    finally:
        if wave_file is not None:
            wave_file.close()
        for stream in streams:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
        audio.terminate()

    try:
        if not wrote_frames:
            raise RuntimeError("La grabación no contiene muestras de audio.")
        ffmpeg = get_ffmpeg_binary()
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(temp_wav),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "96k",
                "-ar",
                "44100",
                str(output_mp3),
            ],
            check=True,
        )
    finally:
        temp_wav.unlink(missing_ok=True)
        stop_file.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Worker WASAPI de ClassAnalizer")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", choices=("meet", "mic", "both"), required=True)
    parser.add_argument("--stop-file", type=Path, required=True)
    args = parser.parse_args()
    record_wasapi_process(args.output, args.source, args.stop_file)


if __name__ == "__main__":
    main()
