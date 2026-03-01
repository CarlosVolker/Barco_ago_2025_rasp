import unittest

from src.edge_agent.video.pipeline import VideoPipeline


class TestVideoPipelineProfiles(unittest.TestCase):
    def test_balanced_profile_command(self):
        pipeline = VideoPipeline(profile="balanced")
        cmd = pipeline.build_linux_cmd()
        self.assertIn("1280", cmd)
        self.assertIn("720", cmd)
        self.assertIn("2500000", cmd)

    def test_switch_to_low_profile(self):
        pipeline = VideoPipeline(profile="balanced")
        pipeline.set_profile("low")
        cmd = pipeline.build_linux_cmd()
        self.assertIn("640", cmd)
        self.assertIn("360", cmd)
        self.assertIn("700000", cmd)

    def test_unknown_profile_falls_back_to_balanced(self):
        pipeline = VideoPipeline(profile="unknown")
        cmd = pipeline.build_linux_cmd()
        self.assertIn("1280", cmd)
        self.assertIn("720", cmd)


if __name__ == "__main__":
    unittest.main()
