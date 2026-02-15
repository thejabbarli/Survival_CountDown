import os
import tempfile
import shutil
from pathlib import Path
from typing import List
from PIL import Image

from moviepy import ImageSequenceClip


class Exporter:
    """Exports rendered frames to video file."""

    def __init__(
            self,
            fps: int = 60,
            output_dir: Path = Path("output"),
            codec: str = "libx264"
    ):
        self.fps = fps
        self.output_dir = Path(output_dir)
        self.codec = codec

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
            self,
            frames: List[Image.Image],
            filename: str,
            audio_path: Path = None
    ) -> Path:
        """
        Export frames to MP4 video.

        Args:
            frames: List of PIL Image frames
            filename: Output filename (without extension)
            audio_path: Optional path to audio file (for Phase 2)

        Returns:
            Path to the exported video file
        """
        output_path = self.output_dir / f"{filename}.mp4"

        # Create temporary directory for frame images
        temp_dir = tempfile.mkdtemp()

        try:
            # Save frames as images
            frame_paths = []
            for i, frame in enumerate(frames):
                frame_path = os.path.join(temp_dir, f"frame_{i:06d}.png")
                frame.save(frame_path)
                frame_paths.append(frame_path)

            # Create video from frames
            clip = ImageSequenceClip(frame_paths, fps=self.fps)

            # Write video file
            clip.write_videofile(
                str(output_path),
                codec=self.codec,
                audio=str(audio_path) if audio_path else None,
                logger=None
            )

            clip.close()

        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

        return output_path
