from pydub import AudioSegment
import random
import os

class VolumeVariationProcessor:
    def __init__(self, output_dir="temp_test_files"):
        """
        Initialize the VolumeVariationProcessor.
        
        Args:
            output_dir (str): Directory to save output audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_volume_variants(self, audio_path, save_intermediate=True):
        """
        Create high and low volume variants of the input audio.
        
        Args:
            audio_path (str): Path to the input audio file
            save_intermediate (bool): Whether to save individual variant files
            
        Returns:
            tuple: (high_audio, low_audio) - AudioSegment objects
        """
        # Load audio
        audio = AudioSegment.from_file(audio_path)
        
        # Generate random volume modifications
        high_db = random.uniform(6, 8)      # Random between 4-8 dB increase
        low_db = random.uniform(-8, -6)     # Random between -8 to -4 dB decrease
        
        # Create volume variants
        louder = audio + high_db
        quieter = audio + low_db
        
        # Save intermediate files if requested
        if save_intermediate:
            base_name = audio_path.split('/')[-1].split('.')[0]
            louder.export(f"{self.output_dir}/{base_name}_louder.wav", format="wav")
            quieter.export(f"{self.output_dir}/{base_name}_quieter.wav", format="wav")
        
        return louder, quieter
    
    def concatenate_audio_three_style(self, audio_path, style_order="high-low-medium"):
        """
        Create a three-style concatenated audio file.
        
        Args:
            audio_path (str): Path to the input audio file
            style_order (str): Order of concatenation, e.g., "high-low-medium"
            
        Returns:
            str: Path to the concatenated audio file
        """
        # Create volume variants
        high_audio, low_audio = self.create_volume_variants(audio_path, save_intermediate=False)
        
        # Load original audio
        original_audio = AudioSegment.from_file(audio_path)
        
        # Create style mapping
        style_map = {
            "high": high_audio,
            "low": low_audio,
            "medium": original_audio
        }
        
        # Parse the style order
        styles = style_order.lower().split("-")
        
        # Concatenate audio in the specified order
        concatenated_audio = sum([style_map[style] for style in styles], AudioSegment.empty())
        
        # Save concatenated audio
        base_name = audio_path.split('/')[-1].split('.')[0]
        output_path = f"{self.output_dir}/{base_name}-volume_variation-{style_order}.wav"
        concatenated_audio.export(output_path, format="wav")
        
        return output_path

if __name__ == "__main__":
    processor = VolumeVariationProcessor(output_dir = "/wekafs/ict/achaubey/emotion_reasoning/speech_llm/code/speech_tts/hallucinated_sample_generation/tmp")
    processor.concatenate_audio_three_style("/wekafs/ict/achaubey/emotion_reasoning/speech_llm/data/MMSU/audio/accent_identification_58df4754-7cb1-4e80-a976-424895cf9aa5.wav", style_order = "high-low-medium")