import numpy as np
import soundfile as sf
import librosa
import pyworld as pw
import os
import random

class IntonationVariationProcessor:
    def __init__(self, output_dir="temp_test_files"):
        """
        Initialize the IntonationVariationProcessor.
        
        Args:
            output_dir (str): Directory to save output audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def apply_intonation(self, audio_path, pattern="rising", semitones=6.0, frame_period=5.0):
        """
        Apply intonation pattern to the entire audio.
        
        Args:
            audio_path (str): Path to the input audio file
            pattern (str): Intonation pattern - "rising", "falling", "rise-fall", "fall-rise"
            semitones (float): Peak magnitude in semitones (use 3-8 typically)
            frame_period (float): WORLD frame hop in ms
            
        Returns:
            tuple: (modified_audio, fs) - numpy array and sample rate
        """
        # 1) Load
        x, fs = librosa.load(audio_path, sr=None)
        x = x.astype(np.float64)

        # 2) WORLD analysis
        f0, t = pw.harvest(x, fs, frame_period=frame_period)         # raw F0 track
        sp = pw.cheaptrick(x, f0, t, fs)                             # spectral envelope
        ap = pw.d4c(x, f0, t, fs)                                    # aperiodicity

        n = len(f0)
        hop = int(round(frame_period * fs / 1000.0))
        total_ms = len(x) * 1000.0 / fs

        # 3) Build a semitone curve over frames (0 where unmodified)
        semitone_curve = np.zeros(n, dtype=np.float64)

        # Always use entire region
        start_f, end_f = 0, n
        L = max(1, end_f - start_f)

        # Smooth shaping helpers
        def smooth_ramp_up(m):   # 0→1
            x = np.linspace(-3, 3, m)
            return 1.0 / (1.0 + np.exp(-x))
        def smooth_ramp_down(m): # 1→0
            return smooth_ramp_up(m)[::-1]

        # 4) Fill semitone curve by pattern
        if pattern == "rising":
            ramp = smooth_ramp_up(L)
            semitone_curve[start_f:end_f] = ramp * semitones
        elif pattern == "falling":
            ramp = smooth_ramp_down(L)
            semitone_curve[start_f:end_f] = ramp * semitones
        elif pattern == "rise-fall":
            half = L // 2
            up = smooth_ramp_up(max(1, half))
            down = smooth_ramp_down(L - half)
            curve = np.concatenate([up, down])
            curve = (curve - curve.min()) / max(1e-8, (curve.max() - curve.min()))  # 0..1
            curve = (curve * 2 - 1) * semitones  # -st .. +st
            semitone_curve[start_f:end_f] = curve
        elif pattern == "fall-rise":
            half = L // 2
            down = smooth_ramp_down(max(1, half))
            up = smooth_ramp_up(L - half)
            curve = np.concatenate([down, up])
            curve = (curve - curve.min()) / max(1e-8, (curve.max() - curve.min()))
            curve = (curve * 2 - 1) * semitones
            semitone_curve[start_f:end_f] = curve
        else:
            raise ValueError("Unknown pattern")

        # 5) Apply only to voiced frames (f0>0)
        new_f0 = f0.copy()
        # Convert semitone shift to multiplicative factor
        factors = 2.0 ** (semitone_curve / 12.0)
        voiced = new_f0 > 0
        new_f0[voiced] = new_f0[voiced] * factors[voiced]

        # 6) Resynthesize
        y = pw.synthesize(new_f0, sp, ap, fs).astype(np.float32)
        
        return y, fs
    
    def convert_to_intonation(self, audio_path, pattern="rising", semitones=None):
        """
        Convert the given audio to a specific intonation pattern.
        
        Args:
            audio_path (str): Path to the input audio file
            pattern (str): Intonation pattern - "rising", "falling", "rise-fall", "fall-rise"
            semitones (float): Peak magnitude in semitones (if None, uses random value between 4.0-7.0)
            
        Returns:
            str: Path to the output audio file with applied intonation
        """
        ## check for valid pattern
        valid_patterns = ["rising", "falling", "rise-fall", "fall-rise"]
        if pattern not in valid_patterns:
            raise ValueError(f"Invalid pattern: {pattern}. Valid patterns for intonation variation are: {valid_patterns}")
        
        # Generate random semitone modification if not provided
        if semitones is None:
            semitones = round(random.uniform(7.0, 9.0), 2)
        
        # Apply intonation pattern
        modified_audio, fs = self.apply_intonation(audio_path, pattern, semitones)
        
        # Save the modified audio
        base_name = audio_path.split('/')[-1].split('.')[0]
        output_path = f"{self.output_dir}/{base_name}-intonation_variation-{pattern}.wav"
        sf.write(output_path, modified_audio, fs)
        
        
        return output_path

if __name__ == "__main__":
    processor = IntonationVariationProcessor(output_dir = "/wekafs/ict/achaubey/emotion_reasoning/speech_llm/code/speech_tts/hallucinated_sample_generation/tmp")
    
    # Convert audio to rising intonation
    processor.convert_to_intonation("/wekafs/ict/achaubey/emotion_reasoning/speech_llm/data/MMSU/audio/accent_identification_58df4754-7cb1-4e80-a976-424895cf9aa5.wav", pattern="fall-rise")
