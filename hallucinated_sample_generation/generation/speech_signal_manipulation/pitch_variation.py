import librosa
import pyworld as pw
import numpy as np
import soundfile as sf
import os
import random
from IPython.display import Audio, display
import subprocess

from pydub import AudioSegment, silence

class PitchVariationProcessor:
    def __init__(self, output_dir="temp_test_files"):
        """
        Initialize the PitchVariationProcessor.
        
        Args:
            output_dir (str): Directory to save output audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_pitch_variants(self, audio_path, save_intermediate=True):
        """
        Create high and low pitch variants of the input audio.
        
        Args:
            audio_path (str): Path to the input audio file
            save_intermediate (bool): Whether to save individual variant files
            
        Returns:
            tuple: (high_audio, low_audio, fs) - numpy arrays and sample rate
        """
        # Load audio (no resampling to keep original fs)
        x, fs = librosa.load(audio_path, sr=None)
        
        # Convert to float64 for PyWORLD
        x = x.astype(np.float64)
        
        # Extract WORLD features
        _f0, t = pw.dio(x, fs)               # Step 1: raw pitch
        f0 = pw.stonemask(x, _f0, t, fs)     # Step 2: refine pitch
        sp = pw.cheaptrick(x, f0, t, fs)     # Step 3: spectral envelope
        ap = pw.d4c(x, f0, t, fs)            # Step 4: aperiodicity
        
        # Generate random pitch modifications
        high_factor = random.uniform(1.4, 1.6)  # Random between 1.4-1.6
        low_factor = random.uniform(0.7, 0.8)   # Random between 0.5-0.7
        
        # Create pitch variants
        f0_high = f0 * high_factor
        f0_low = f0 * low_factor
        
        # Resynthesize
        y_high = pw.synthesize(f0_high, sp, ap, fs, pw.default_frame_period)
        y_low = pw.synthesize(f0_low, sp, ap, fs, pw.default_frame_period)
        
        # Save intermediate files if requested
        if save_intermediate:
            base_name = audio_path.split('/')[-1].split('.')[0]
            sf.write(f"{self.output_dir}/{base_name}_high.wav", y_high.astype(np.float32), fs)
            sf.write(f"{self.output_dir}/{base_name}_low.wav", y_low.astype(np.float32), fs)
        
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
        # Create pitch variants
        high_audio, low_audio, fs = self.create_pitch_variants(audio_path, save_intermediate=False)
        
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
        output_path = f"{self.output_dir}/{base_name}-pitch_variation-{style_order}.wav"
        sf.write(output_path, concatenated_audio.astype(np.float32), fs)
        
        return output_path

if __name__ == "__main__":
    processor = PitchVariationProcessor(output_dir = "/wekafs/ict/achaubey/emotion_reasoning/speech_llm/code/speech_tts/hallucinated_sample_generation/tmp")
    processor.concatenate_audio_three_style("/wekafs/ict/achaubey/emotion_reasoning/speech_llm/data/MMSU/audio/accent_identification_58df4754-7cb1-4e80-a976-424895cf9aa5.wav", style_order = "high-low-medium")