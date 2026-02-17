"""Video exporter using MoviePy - memory efficient."""

import shutil
from pathlib import Path
from typing import List, Optional, Callable, Union
from PIL import Image


class Exporter:
    """Exports frames to video."""

    def __init__(
        self,
        fps: int = 60,
        output_dir: Path = Path("output")
    ):
        self.fps = fps
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        frames: List[Image.Image],
        filename: str = "output.mp4",
        audio: Optional[Union[Path, str]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Path:
        """Export frames to video file.

        Writes frames to disk first to avoid memory issues with large videos.
        """
        try:
            from moviepy import ImageSequenceClip, AudioFileClip
        except ImportError:
            from moviepy.editor import ImageSequenceClip, AudioFileClip

        # Ensure .mp4 extension
        if not filename.endswith('.mp4'):
            filename = filename + '.mp4'

        output_path = self.output_dir / filename

        # Create temp directory for frames
        temp_dir = self.output_dir / "_temp_frames"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        try:
            # Write frames to disk as JPEG (smaller, faster)
            print(f"  Saving {len(frames)} frames to disk...")
            frame_paths = []

            for i, frame in enumerate(frames):
                if frame.mode != 'RGB':
                    frame = frame.convert('RGB')

                frame_path = temp_dir / f"frame_{i:06d}.jpg"
                frame.save(frame_path, "JPEG", quality=95)
                frame_paths.append(str(frame_path))

                # Progress
                if i % 200 == 0:
                    print(f"    {i}/{len(frames)} frames saved")

                # Free memory
                frames[i] = None

            print(f"  Encoding video...")

            # Create clip from file paths (memory efficient)
            clip = ImageSequenceClip(frame_paths, fps=self.fps)

            # Add audio if provided
            audio_path = Path(audio) if audio else None
            if audio_path and audio_path.exists():
                audio_clip = AudioFileClip(str(audio_path))

                if audio_clip.duration > clip.duration:
                    try:
                        audio_clip = audio_clip.subclipped(0, clip.duration)
                    except AttributeError:
                        audio_clip = audio_clip.subclip(0, clip.duration)

                try:
                    clip = clip.with_audio(audio_clip)
                except AttributeError:
                    clip = clip.set_audio(audio_clip)

            # Write video
            clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac' if audio_path else None,
                fps=self.fps,
                preset='fast',
                threads=4,
                logger=None
            )

            clip.close()

        finally:
            # Clean up temp frames
            print(f"  Cleaning up temp files...")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

        return output_path

    def export_frames_only(
        self,
        frames: List[Image.Image],
        prefix: str = "frame"
    ) -> List[Path]:
        """Export frames as individual images."""
        frames_dir = self.output_dir / "frames"
        frames_dir.mkdir(exist_ok=True)

        paths = []
        for i, frame in enumerate(frames):
            path = frames_dir / f"{prefix}_{i:05d}.png"
            frame.save(path)
            paths.append(path)

        return paths
