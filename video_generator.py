"""
🎮 Larva Character Video Generator - 360p
Karakter bergerak frame by frame sesuai cerita
"""

import os
import re
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

try:
    from moviepy import AudioFileClip, ImageSequenceClip
except:
    from moviepy.editor import AudioFileClip, ImageSequenceClip

# ============ KONFIGURASI ============
WIDTH = 360   # 360p
HEIGHT = 640  # 9:16 ratio
FPS = 30

class CharacterAnimationParser:
    """Parse file karakter menjadi animasi"""

    def __init__(self, assets_folder="larva_assets"):
        self.assets_folder = assets_folder
        self.characters = {}
        self.parse()

    def parse(self):
        """Parse semua file PNG"""
        for root, dirs, files in os.walk(self.assets_folder):
            for file in files:
                if file.endswith('.png'):
                    parts = file.replace('.png', '').split('_')

                    if len(parts) >= 3:
                        # Deteksi karakter (1 atau 2 kata)
                        if len(parts) >= 4 and parts[1] in ['knight', 'warrior', 'hulk', 'zoro', 'viking', 'termi', 'spider', 'ninja', 'kungfu', 'iron']:
                            char_name = '_'.join(parts[:2])
                            anim_name = parts[2]
                        else:
                            char_name = parts[0]
                            anim_name = parts[1]

                        if char_name not in self.characters:
                            self.characters[char_name] = {}

                        if anim_name not in self.characters[char_name]:
                            self.characters[char_name][anim_name] = []

                        self.characters[char_name][anim_name].append(os.path.join(root, file))

        # Sort
        for char in self.characters:
            for anim in self.characters[char]:
                self.characters[char][anim].sort()

    def get_animation_frames(self, char_name, anim_name):
        """Dapatkan frames untuk animasi"""
        if char_name in self.characters:
            if anim_name in self.characters[char_name]:
                return self.characters[char_name][anim_name]

        # Fallback: cari animasi apapun
        if char_name in self.characters:
            for anim in self.characters[char_name]:
                return self.characters[char_name][anim]

        # Fallback: cari karakter apapun
        for char in self.characters:
            for anim in self.characters[char]:
                return self.characters[char][anim]

        return []

class StoryActionDetector:
    """Deteksi aksi dari teks cerita"""

    ACTION_MAP = {
        'walk': ['berjalan', 'jalan', 'melangkah', 'pergi', 'datang'],
        'run': ['berlari', 'lari', 'cepat', 'buru', 'kejar'],
        'stand': ['berdiri', 'diam', 'berhenti', 'menunggu'],
        'attack': ['menyerang', 'serang', 'pukul', 'tendang', 'lawan', 'hajar'],
        'skill': ['skill', 'jurus', 'sihir', 'magic', 'power', 'spesial'],
        'damage': ['terluka', 'sakit', 'kena', 'terkena', 'jatuh'],
        'death': ['mati', 'tewas', 'kalah', 'hancur', 'tumbang'],
        'idle': ['diam', 'santai', 'istirahat', 'tidur'],
    }

    CHAR_MAP = {
        'black_knight': ['black knight', 'knight', 'ksatria hitam'],
        'rainbow_warrior': ['rainbow', 'pelangi', 'warrior'],
        'red': ['red', 'merah'],
        'yellow': ['yellow', 'kuning'],
    }

    def detect_action(self, text):
        text_lower = text.lower()
        for action, keywords in self.ACTION_MAP.items():
            for kw in keywords:
                if kw in text_lower:
                    return action
        return 'stand'

    def detect_character(self, text):
        text_lower = text.lower()
        for char, keywords in self.CHAR_MAP.items():
            for kw in keywords:
                if kw in text_lower:
                    return char
        return None

class AnimatedLarvaGenerator:
    """Generator video dengan karakter bergerak"""

    def __init__(self, assets_folder="larva_assets"):
        self.parser = CharacterAnimationParser(assets_folder)
        self.detector = StoryActionDetector()
        self.watermark_text = "YT: CeritaMistery | Penulis: Yad | Editor: Yad"

        print(f"✅ {len(self.parser.characters)} karakter loaded")

    def create_background(self, frame_num=0):
        """Background 360p"""
        img = Image.new("RGB", (WIDTH, HEIGHT), (15, 15, 35))
        draw = ImageDraw.Draw(img)

        # Gradient
        for y in range(HEIGHT):
            factor = y / HEIGHT
            r = int(15 * (1 - factor * 0.5))
            g = int(15 * (1 - factor * 0.5))
            b = int(35 * (1 - factor * 0.5))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        # Ground
        draw.rectangle([(0, HEIGHT-80), (WIDTH, HEIGHT)], fill=(40, 35, 25))

        return img

    def add_character_frame(self, background, char_name, anim_name, frame_num=0):
        """Tambah karakter dengan animasi"""
        frames = self.parser.get_animation_frames(char_name, anim_name)

        if not frames:
            return background

        # Loop animasi
        frame_idx = frame_num % len(frames)
        sprite_path = frames[frame_idx]

        try:
            sprite = Image.open(sprite_path)
            sprite = sprite.convert("RGBA")

            # Resize untuk 360p
            max_w = int(WIDTH * 0.6)
            max_h = int(HEIGHT * 0.4)
            ratio = min(max_w / sprite.width, max_h / sprite.height)
            new_w = int(sprite.width * ratio)
            new_h = int(sprite.height * ratio)
            sprite = sprite.resize((new_w, new_h), Image.LANCZOS)

            # Posisi tengah bawah
            x = (WIDTH - new_w) // 2
            y = HEIGHT - new_h - 60

            background.paste(sprite, (x, y), sprite)
        except:
            pass

        return background

    def add_watermark(self, image):
        """Watermark kecil"""
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()

        draw.rounded_rectangle([10, HEIGHT-50, WIDTH-10, HEIGHT-5], radius=8, fill=(0,0,0,120))

        text = "YT: CeritaMistery | Penulis: Yad"
        bbox = draw.textbbox((0,0), text, font=font)
        x = (WIDTH - (bbox[2]-bbox[0])) // 2
        draw.text((x+1, HEIGHT-40), text, fill="black", font=font)
        draw.text((x, HEIGHT-42), text, fill=(255,255,255,180), font=font)

        return image

    def generate_video(self, cerita, duration=None):
        """Generate video dari cerita"""

        # TTS
        tts = gTTS(text=cerita, lang="id", slow=False)
        tts.save("temp_audio.mp3")
        audio = AudioFileClip("temp_audio.mp3")

        if not duration:
            duration = audio.duration

        # Split cerita menjadi kalimat
        sentences = [s.strip() for s in re.split(r'[.!?]+', cerita) if s.strip()]

        # Buat scene untuk setiap kalimat
        scenes = []
        for sentence in sentences:
            action = self.detector.detect_action(sentence)
            character = self.detector.detect_character(sentence)

            scenes.append({
                'text': sentence,
                'action': action,
                'character': character,
                'duration': max(len(sentence.split()) / 2.5, 1.0)
            })

        print(f"📝 {len(scenes)} scenes:")
        for i, scene in enumerate(scenes):
            print(f"   Scene {i+1}: [{scene['character'] or 'default'}] {scene['action']}")

        # Generate frames
        total_frames = int(duration * FPS)
        frames_per_scene = total_frames // len(scenes) if scenes else total_frames

        print(f"🎨 {total_frames} frames...")

        frames = []
        for frame_num in range(total_frames):
            scene_idx = min(frame_num // frames_per_scene, len(scenes) - 1)
            scene = scenes[scene_idx]

            # Background
            bg = self.create_background(frame_num)

            # Tambah karakter
            char_name = scene['character']
            action = scene['action']

            if char_name:
                bg = self.add_character_frame(bg, char_name, action, frame_num)
            else:
                # Coba semua karakter
                for char in self.parser.characters:
                    bg = self.add_character_frame(bg, char, action, frame_num)
                    break

            # Watermark
            bg = self.add_watermark(bg)

            frames.append(np.array(bg))

            if frame_num % 100 == 0:
                print(f"  Frame {frame_num}/{total_frames}")

        # Buat video
        print("📹 Creating video...")
        video = ImageSequenceClip(frames, fps=FPS)
        video = video.with_audio(audio)

        os.makedirs("output", exist_ok=True)
        output = "output/larva_animated.mp4"
        video.write_videofile(output, fps=FPS, codec="libx264", audio_codec="aac", bitrate="800k", preset="ultrafast")

        video.close()
        audio.close()

        return output

if __name__ == "__main__":
    generator = AnimatedLarvaGenerator()

    cerita = "Black Knight berjalan di hutan. Dia berhenti dan berdiri. Tiba-tiba dia berlari menyerang musuh."

    result = generator.generate_video(cerita)
    print(f"\n✅ Video: {result}")
