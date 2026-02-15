"""Manual beat tapper with built-in music playback."""

import time
import argparse
import os
import msvcrt

def quantize_beats(timestamps, threshold=0.1):
    """Snap small timing errors to grid, keep intentional gaps."""
    if len(timestamps) < 3:
        return timestamps

    gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    gaps_sorted = sorted(gaps)
    median_gap = gaps_sorted[len(gaps_sorted)//2]

    result = [timestamps[0]]
    for i, gap in enumerate(gaps):
        if abs(gap - median_gap) < threshold:
            result.append(result[-1] + median_gap)
        elif abs(gap - median_gap*2) < threshold:
            result.append(result[-1] + median_gap*2)
        elif abs(gap - median_gap*0.5) < threshold:
            result.append(result[-1] + median_gap*0.5)
        else:
            result.append(result[-1] + gap)

    return result

def play_music(music_path):
    """Start playing music, return True if successful."""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play()
        return True
    except ImportError:
        print("ERROR: pygame not installed. Run: pip install pygame")
        return False
    except Exception as e:
        print(f"ERROR: Could not play music: {e}")
        return False

def stop_music():
    """Stop music playback."""
    try:
        import pygame
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass

def countdown(seconds=3):
    """Visual countdown."""
    print()
    for i in range(seconds, 0, -1):
        print(f"  {i}...", flush=True)
        time.sleep(1)
    print("  GO!", flush=True)
    print()

def main():
    parser = argparse.ArgumentParser(description="Tap beats manually")
    parser.add_argument("--output", "-o", default="beats.txt", help="Output filename")
    parser.add_argument("--count", "-c", type=int, default=None, help="Stop after N taps")
    parser.add_argument("--fps", type=int, default=60, help="Video FPS")
    parser.add_argument("--quantize", "-q", action="store_true", help="Snap small errors to grid")
    parser.add_argument("--music", "-m", type=str, default=None, help="Play music internally (auto-sync)")
    parser.add_argument("--countdown", type=int, default=3, help="Countdown seconds before start")
    args = parser.parse_args()

    # Create beats folder
    beats_dir = "beats"
    os.makedirs(beats_dir, exist_ok=True)
    output_path = os.path.join(beats_dir, args.output)

    print("=" * 50)
    print("MANUAL BEAT TAPPER")
    print("=" * 50)
    print()

    if args.music:
        print(f"Music: {args.music}")
        print(f"Countdown: {args.countdown}s")
        print()
        print("Press SPACE for each elimination beat")
        print("Press Q to quit")
    else:
        print("Mode: External music (you play it yourself)")
        print()
        print("Option A: Press ENTER when your music starts")
        print("Option B: Press SPACE on first beat (that beat = frame 0)")
        print()
        print("Then keep pressing SPACE for each beat. Q to quit.")

    print()
    if args.count:
        print(f"Will stop after {args.count} taps")
    if args.quantize:
        print("Quantize: ON")
    print()

    timestamps = []
    start_time = None
    first_space_is_start = False

    if args.music:
        # Internal music mode
        input("Press ENTER to start countdown...")
        countdown(args.countdown)

        if not play_music(args.music):
            return

        start_time = time.time()
        print("Music playing! Tap SPACE for each beat...", flush=True)
        print()
    else:
        # External music mode
        print("Waiting... (ENTER = music started, SPACE = first beat)", flush=True)

        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getch()

                if ch in (b'\x00', b'\xe0'):
                    msvcrt.getch()
                    continue

                if ch == b'\r' or ch == b'\n':  # ENTER
                    start_time = time.time()
                    print("\nGO! Tap SPACE for each beat...", flush=True)
                    print()
                    break
                elif ch == b' ' or ch == b' '[0:1]:  # SPACE
                    start_time = time.time()
                    timestamps.append(0.0)
                    first_space_is_start = True
                    print(f"\n  Beat 1/{args.count or '?'}: 0.00s (frame 0)  [START]", flush=True)
                    break
                elif ch.lower() == b'q':
                    print("Cancelled.")
                    return
            time.sleep(0.005)

    # Main tapping loop
    try:
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getch()

                if ch in (b'\x00', b'\xe0'):
                    msvcrt.getch()
                    continue

                try:
                    key = ch.decode('utf-8').lower()
                except:
                    continue

                if key == ' ':
                    elapsed = time.time() - start_time
                    timestamps.append(elapsed)
                    frame = int(elapsed * args.fps)

                    if len(timestamps) >= 2:
                        gap = timestamps[-1] - timestamps[-2]
                        bpm = 60 / gap if gap > 0 else 0
                        gap_info = f"  gap: {gap:.2f}s ({bpm:.0f} BPM)"
                    else:
                        gap_info = ""

                    remaining = args.count - len(timestamps) if args.count else "?"
                    print(f"  Beat {len(timestamps)}/{args.count or '?'}: {elapsed:.2f}s (frame {frame}){gap_info}  [{remaining} left]", flush=True)

                    if args.count and len(timestamps) >= args.count:
                        print(f"\nDone!", flush=True)
                        break

                elif key == 'q':
                    print("\nQuit.", flush=True)
                    break

            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\nInterrupted.", flush=True)

    finally:
        if args.music:
            stop_music()

    if not timestamps:
        print("No beats recorded.")
        return

    # Quantize if requested
    if args.quantize and len(timestamps) >= 3:
        print("\nQuantizing...", flush=True)
        timestamps = quantize_beats(timestamps)
        print("Done.", flush=True)

    # Summary
    if len(timestamps) >= 2:
        gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_gap = sum(gaps) / len(gaps)
        print(f"\nAverage: {avg_gap:.2f}s ({60/avg_gap:.0f} BPM)")
    print(f"Duration: {timestamps[-1]:.1f}s")
    print(f"Beats: {len(timestamps)}")

    # Save
    with open(output_path, 'w') as f:
        for t in timestamps:
            f.write(f"{int(t * args.fps)}\n")

    print(f"\nSaved to: {output_path}")

    # Show run command
    music_arg = args.music or "sounds/music/YOUR_MUSIC.mp3"
    print(f"\nRun:")
    print(f"  python main.py --beats {output_path} --music {music_arg} --count {len(timestamps) + 1}")

if __name__ == "__main__":
    main()
