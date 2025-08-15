import librosa
import pyworld as pw
import numpy as np
import soundfile as sf
import os
import random

class VocalRangeVariationProcessor:
    def __init__(self, output_dir="temp_test_files"):
        """
        Initialize the VocalRangeVariationProcessor.
        
        Args:
            output_dir (str): Directory to save output audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def change_vocal_range(self, audio_path, scale):
        """
        Change the vocal range of the audio by scaling the F0 variation.
        
        Args:
            audio_path (str): Path to the input audio file
            scale (float): Scale factor for vocal range (higher = more expressive, lower = more monotone)
            
        Returns:
            tuple: (modified_audio, fs) - numpy array and sample rate
        """
        x, fs = librosa.load(audio_path, sr=None)
        x = x.astype(np.float64)

        # Extract features
        _f0, t = pw.dio(x, fs)
        f0 = pw.stonemask(x, _f0, t, fs)
        sp = pw.cheaptrick(x, f0, t, fs)
        ap = pw.d4c(x, f0, t, fs)

        # Change vocal range
        mean_f0 = np.mean(f0[f0 > 0])  # ignore unvoiced frames
        new_f0 = np.where(
            f0 > 0,
            mean_f0 + scale * (f0 - mean_f0),
            0
        )

        # Synthesize
        y = pw.synthesize(new_f0, sp, ap, fs)
        return y, fs
    
    def create_vocal_range_variants(self, audio_path, save_intermediate=True):
        """
        Create high and low vocal range variants of the input audio.
        
        Args:
            audio_path (str): Path to the input audio file
            save_intermediate (bool): Whether to save individual variant files
            
        Returns:
            tuple: (high_audio, low_audio, fs) - numpy arrays and sample rate
        """
        # Generate random vocal range modifications
        # high_scale = round(random.uniform(2.0, 3.0), 2)    # Random between 2.0-3.0 (more expressive)
        # low_scale = round(random.uniform(0.2, 0.4), 2)     # Random between 0.2-0.4 (more monotone)
        high_scale = 3.0
        low_scale = 0.2
        
        # Create vocal range variants
        y_high, fs = self.change_vocal_range(audio_path, high_scale)
        y_low, fs = self.change_vocal_range(audio_path, low_scale)
        
        # Save intermediate files if requested
        if save_intermediate:
            base_name = audio_path.split('/')[-1].split('.')[0]
            sf.write(f"{self.output_dir}/{base_name}_high_range.wav", y_high.astype(np.float32), fs)
            sf.write(f"{self.output_dir}/{base_name}_low_range.wav", y_low.astype(np.float32), fs)
        
        return y_high, y_low, fs
    
    def concatenate_audio_three_style(self, audio_path, style_order="high-low-medium"):
        """
        Create a three-style concatenated audio file.
        
        Args:
            audio_path (str): Path to the input audio file
            style_order (str): Order of concatenation, e.g., "high-low-medium"
            
        Returns:
            str: Path to the concatenated audio file
        """
        # Create vocal range variants
        high_audio, low_audio, fs = self.create_vocal_range_variants(audio_path, save_intermediate=False)
        
        # Load original audio
        original_audio, _ = librosa.load(audio_path, sr=fs)
        
        # Create style mapping
        style_map = {
            "high": high_audio,
            "low": low_audio,
            "medium": original_audio
        }
        
        # Parse the style order
        styles = style_order.lower().split("-")
        
        # Concatenate audio in the specified order
        concatenated_audio = np.concatenate([style_map[style] for style in styles])
        
        # Save concatenated audio
        base_name = audio_path.split('/')[-1].split('.')[0]
        output_path = f"{self.output_dir}/vocal_range_comparison__{base_name}-{style_order}.wav"
        sf.write(output_path, concatenated_audio.astype(np.float32), fs)
        
        return output_path

if __name__ == "__main__":
    processor = VocalRangeVariationProcessor(output_dir = "/wekafs/ict/achaubey/emotion_reasoning/speech_llm/code/speech_tts/hallucinated_sample_generation/tmp")
    processor.concatenate_audio_three_style("/wekafs/ict/achaubey/emotion_reasoning/speech_llm/data/MMSU/audio/accent_identification_58df4754-7cb1-4e80-a976-424895cf9aa5.wav", style_order = "high-low-medium")
