import os
import json
import argparse
import unittest
from unittest.mock import MagicMock, patch
from src.domain.entities import ScriptScene

# Mocking parts of main to test the saving logic
def save_script_logic(final_state, args):
    if final_state.get('final_script'):
        output_dir = "reel_scripts"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json_output = [scene.model_dump() for scene in final_state['final_script']]
            json.dump(json_output, f, indent=2, ensure_ascii=False)
        
        # Save text-only version
        text_output_dir = "reel_text"
        os.makedirs(text_output_dir, exist_ok=True)
        text_filename = os.path.splitext(args.output)[0] + ".txt"
        text_output_path = os.path.join(text_output_dir, text_filename)
        with open(text_output_path, "w", encoding="utf-8") as f:
            for scene in final_state['final_script']:
                f.write(f"{scene.scene_number} - {scene.spoken_text}\n")
        
        return output_path, text_output_path
    return None, None

class TestOutputSaving(unittest.TestCase):
    def test_save_script_and_text(self):
        # Mock data
        scene1 = ScriptScene(
            scene_number=1,
            visual_cue="Scene 1 visual",
            spoken_text="Hello world",
            text_on_screen="HELLO",
            estimated_duration=5
        )
        scene2 = ScriptScene(
            scene_number=2,
            visual_cue="Scene 2 visual",
            spoken_text="This is a test",
            text_on_screen="TEST",
            estimated_duration=10
        )
        
        final_state = {
            'final_script': [scene1, scene2]
        }
        
        args = MagicMock()
        args.output = "test_reel.json"
        
        # Run logic
        json_path, txt_path = save_script_logic(final_state, args)
        
        # Verify JSON
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['scene_number'], 1)
            self.assertEqual(data[0]['spoken_text'], "Hello world")
        
        # Verify TXT
        self.assertTrue(os.path.exists(txt_path))
        self.assertEqual(txt_path, os.path.join("reel_text", "test_reel.txt"))
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[0].strip(), "1 - Hello world")
            self.assertEqual(lines[1].strip(), "2 - This is a test")
            
        # Cleanup
        if os.path.exists(json_path):
            os.remove(json_path)
        if os.path.exists(txt_path):
            os.remove(txt_path)
        if os.path.exists("reel_scripts") and not os.listdir("reel_scripts"):
            os.rmdir("reel_scripts")
        if os.path.exists("reel_text") and not os.listdir("reel_text"):
            os.rmdir("reel_text")

if __name__ == "__main__":
    unittest.main()
