"""Video export - frames to MP4."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from PIL import Image

# Optional dependency - may not be installed
try:
    from moviepy import ImageSequenceClip, CompositeAudioClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    ImageSequenceClip = None
    CompositeAudioClip = None


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

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        frames: List[Image.Image],
        filename: str,
        audio: Optional['CompositeAudioClip'] = None
    ) -> Path:
        """
        Export frames to MP4 video.

        Args:
            frames: List of PIL Image frames
            filename: Output filename (without extension)
            audio: Optional CompositeAudioClip to merge

        Returns:
            Path to the exported video file
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError(
                "moviepy is required for video export. "
                "Install with: pip install moviepy"
            )
        
        output_path = self.output_dir / f"{filename}.mp4"
        temp_dir = tempfile.mkdtemp()

        try:
            # Save frames as images
            frame_paths = []
            for i, frame in enumerate(frames):
                frame_path = os.path.join(temp_dir, f"frame_{i:06d}.png")
                frame.save(frame_path)
                frame_paths.append(frame_path)

            # Create video clip
            clip = ImageSequenceClip(frame_paths, fps=self.fps)

            # Add audio if provided
            if audio is not None:
                clip = clip.with_audio(audio)

            # Write video
            clip.write_videofile(
                str(output_path),
                codec=self.codec,
                audio_codec="aac" if audio is not None else None,
                logger="bar"
            )

            clip.close()
            if audio is not None:
                audio.close()

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return output_path
