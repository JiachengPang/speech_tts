import subprocess
import random
import os

class SpeedVariationProcessor:
    def __init__(self, output_dir="temp_test_files"):
        """
        Initialize the SpeedVariationProcessor.
        
        Args:
            output_dir (str): Directory to save output audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_speed_variants(self, audio_path, save_intermediate=True):
        """
        Create fast and slow speed variants of the input audio.
        
        Args:
            audio_path (str): Path to the input audio file
            save_intermediate (bool): Whether to save individual variant files
            
        Returns:
            tuple: (fast_path, slow_path) - paths to the generated files
        """
        
        # Generate random speed modifications
        fast_factor = round(random.uniform(1.15, 1.25), 2)   # Random between 1.15-1.25 (15-25% faster)
        slow_factor = round(random.uniform(0.75, 0.85), 2)   # Random between 0.75-0.85 (15-25% slower)
        
        base = os.path.splitext(os.path.basename(audio_path))[0]
        fast_path = f"{self.output_dir}/{base}_faster.wav"
        slow_path = f"{self.output_dir}/{base}_slower.wav"
        
        subprocess.run(["sox", "-t", "wav", audio_path, fast_path, "tempo", str(fast_factor)], check=True, capture_output=True)
        
        subprocess.run(["sox", "-t", "wav", audio_path, slow_path, "tempo", str(slow_factor)], check=True, capture_output=True)
        
        return fast_path, slow_path
            
    
    def concatenate_audio_three_style(self, audio_path, style_order="fast-slow-medium"):
        """
        Create a three-style concatenated audio file.
        
        Args:
            audio_path (str): Path to the input audio file
            style_order (str): Order of concatenation, e.g., "fast-slow-medium"
            
        Returns:
            str: Path to the concatenated audio file
        """
        # Create speed variants
        fast_path, slow_path = self.create_speed_variants(audio_path, save_intermediate=False)
        
        # Create style mapping
        style_map = {
            "fast": fast_path,
            "slow": slow_path,
            "medium": audio_path
        }
        
        # Parse the style order
        styles = style_order.lower().split("-")
        
        # Get the list of files to concatenate in the specified order
        files_to_concat = [style_map[style] for style in styles]
        
        # Save concatenated audio
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"{self.output_dir}/{base_name}-speed_variation-{style_order}.wav"
        
        # Concatenate using sox
        subprocess.run(["sox"] + files_to_concat + [output_path], check=True, capture_output=True)

        ## delete the intermediate files
        os.remove(fast_path)
        os.remove(slow_path)

        return output_path
            

if __name__ == "__main__":
    processor = SpeedVariationProcessor(output_dir = "/wekafs/ict/achaubey/emotion_reasoning/speech_llm/code/speech_tts/hallucinated_sample_generation/tmp")
    
    # Test with a different audio file first
    test_audio = "/wekafs/ict/achaubey/emotion_reasoning/audio_exp/data/seed_examples/237_126133_000007_000001.wav"
    
    processor.concatenate_audio_three_style(test_audio, style_order = "fast-slow-medium")