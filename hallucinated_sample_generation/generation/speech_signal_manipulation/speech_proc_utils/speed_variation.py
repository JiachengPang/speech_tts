import subprocess
import random
import os
import tempfile

class SpeedVariationProcessor:
    def __init__(self, output_dir="temp_test_files"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def convert_to_pcm_wav(self, input_audio):
        temp_wav = os.path.join(tempfile.gettempdir(), f"temp_pcm_{os.path.basename(input_audio)}")
        subprocess.run([
            "ffmpeg", "-y", "-i", input_audio,
            "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
            temp_wav
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return temp_wav

    def create_speed_variants(self, audio_path, save_intermediate=True):
        wav_path = self.convert_to_pcm_wav(audio_path)

        fast_factor = round(random.uniform(1.15, 1.25), 2)
        slow_factor = round(random.uniform(0.75, 0.85), 2)

        base = os.path.splitext(os.path.basename(audio_path))[0]
        fast_path = f"{self.output_dir}/{base}_faster.wav"
        slow_path = f"{self.output_dir}/{base}_slower.wav"

        subprocess.run(["sox", "-t", "wav", wav_path, fast_path, "tempo", str(fast_factor)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["sox", "-t", "wav", wav_path, slow_path, "tempo", str(slow_factor)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(wav_path):
            os.remove(wav_path)

        return fast_path, slow_path

    def concatenate_audio_three_style(self, audio_path, style_order="high-low-medium"):
        fast_path, slow_path = self.create_speed_variants(audio_path, save_intermediate=False)

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"{self.output_dir}/speed_comparison__{base_name}-{style_order}.wav"

        style_map = {
            "high": fast_path,
            "low": slow_path,
            "medium": self.convert_to_pcm_wav(audio_path)
        }

        styles = style_order.lower().split("-")
        files_to_concat = [style_map[style] for style in styles]

        filelist_path = os.path.join(self.output_dir, f"filelist__{base_name}.txt")
        with open(filelist_path, 'w') as f:
            for file in files_to_concat:
                f.write(f"file '{os.path.abspath(file)}'\n")

        # FFmpeg concat
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", filelist_path,
            "-ar", "16000", "-ac", "1", "-sample_fmt", "s16", "-c:a", "pcm_s16le",
            output_path
        ], check=True)

        # Clean up
        os.remove(fast_path)
        os.remove(slow_path)
        os.remove(style_map["medium"])
        os.remove(filelist_path)

        return output_path


if __name__ == "__main__":
    processor = SpeedVariationProcessor(
        output_dir="/wekafs/ict/achaubey/emotion_reasoning/speech_llm/code/speech_tts/hallucinated_sample_generation/tmp"
    )

    test_audio = "/wekafs/ict/achaubey/emotion_reasoning/speech_llm/code/speech_tts/hallucinated_sample_generation/generation/speech_signal_manipulation/tts_outputs/speed/speed/high/speed_high_0_coral.wav"

    processor.concatenate_audio_three_style(test_audio, style_order="high-low-medium")
