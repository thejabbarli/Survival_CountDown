"""Video exporter using MoviePy."""

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
        
        Args:
            frames: List of PIL Image frames
            filename: Output filename (adds .mp4 if missing)
            audio: Path to audio file (optional)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to output video file
        """
        # Try new moviepy import first, then fall back to old
        try:
            from moviepy import ImageSequenceClip, AudioFileClip
        except ImportError:
            try:
                from moviepy.editor import ImageSequenceClip, AudioFileClip
            except ImportError:
                raise ImportError(
                    "moviepy is required for export. Install with: pip install moviepy\n"
                    "If you have moviepy installed, try: pip install --upgrade moviepy"
                )

        import numpy as np

        # Ensure .mp4 extension
        if not filename.endswith('.mp4'):
            filename = filename + '.mp4'
            
        output_path = self.output_dir / filename

        # Convert PIL images to numpy arrays
        frame_arrays = []
        for i, frame in enumerate(frames):
            if frame.mode != 'RGB':
                frame = frame.convert('RGB')
            frame_arrays.append(np.array(frame))
            
            if progress_callback and i % 10 == 0:
                progress_callback(i, len(frames))

        # Create video clip
        clip = ImageSequenceClip(frame_arrays, fps=self.fps)

        # Add audio if provided
        audio_path = Path(audio) if audio else None
        if audio_path and audio_path.exists():
            audio_clip = AudioFileClip(str(audio_path))
            # Trim audio to video length
            if audio_clip.duration > clip.duration:
                # Handle both old and new moviepy API
                try:
                    audio_clip = audio_clip.subclipped(0, clip.duration)
                except AttributeError:
                    audio_clip = audio_clip.subclip(0, clip.duration)
            # Use with_audio for newer moviepy, set_audio for older
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
            preset='medium',
            logger=None
        )

        # Clean up
        clip.close()
        if audio_path and audio_path.exists():
            try:
                audio_clip.close()
            except:
                pass

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
