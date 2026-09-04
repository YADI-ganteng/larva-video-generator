"""
🎮 Larva Video Generator - Complete
Watermark Atas + YADSTORES + Animasi Lambat
"""

import os
import re
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from gtts import gTTS
from io import BytesIO
import requests

try:
    from moviepy import AudioFileClip, ImageSequenceClip
except:
    from moviepy.editor import AudioFileClip, ImageSequenceClip

WIDTH = 360
HEIGHT = 640
FPS = 30
PART_DURATION = 120
CHAR_ANIM_FPS = 8

ASSETS_FOLDER = "larva_assets"

class CharacterParser:
    def __init__(self):
        self.characters = {}
        self.parse()
    
    def parse(self):
        for root, dirs, files in os.walk(ASSETS_FOLDER):
            for file in files:
                if file.endswith('.png'):
                    parts = file.replace('.png', '').split('_')
                    if len(parts) >= 3:
                        if len(parts) >= 4 and parts[1] in ['knight', 'warrior', 'ninja', 'zoro', 'spider', 'viking', 'terminator', 'iron']:
                            char = '_'.join(parts[:2])
                            anim = parts[2]
                        else:
                            char = parts[0]
                            anim = parts[1]
                        
                        if char not in self.characters:
                            self.characters[char] = {}
                        if anim not in self.characters[char]:
                            self.characters[char][anim] = []
                        self.characters[char][anim].append(os.path.join(root, file))
        
        for char in self.characters:
            for anim in self.characters[char]:
                self.characters[char][anim].sort()
        
        print(f"✅ {len(self.characters)} karakter")
    
    def get_frames(self, char, anim):
        if char in self.characters and anim in self.characters[char]:
            return self.characters[char][anim]
        for c in self.characters:
            for a in self.characters[c]:
                return self.characters[c][a]
        return []

class BackgroundDownloader:
    def __init__(self):
        self.cache = {}
    
    def get_bg(self, query):
        if query in self.cache:
            return self.cache[query].copy()
        img = self.download(query)
        self.cache[query] = img
        return img.copy()
    
    def download(self, query):
        for url in [
            f"https://picsum.photos/{WIDTH}/{HEIGHT}?random={random.randint(1,1000)}",
            f"https://source.unsplash.com/{WIDTH}x{HEIGHT}/?{query.replace(' ', '-')}",
        ]:
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                if response.status_code == 200 and len(response.content) > 1000:
                    img = Image.open(BytesIO(response.content))
                    img = img.convert("RGB")
                    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
                    return img
            except:
                continue
        
        img = Image.new("RGB", (WIDTH, HEIGHT), (15, 15, 35))
        draw = ImageDraw.Draw(img)
        for y in range(HEIGHT):
            f = y / HEIGHT
            draw.line([(0, y), (WIDTH, y)], fill=(int(15*(1-f*0.5)), int(15*(1-f*0.5)), int(35*(1-f*0.5))))
        return img

class StoryDetector:
    ACTIONS = {
        'walk': ['berjalan', 'jalan', 'melangkah'],
        'run': ['berlari', 'lari', 'cepat'],
        'stand': ['berdiri', 'diam', 'berhenti'],
        'attack': ['menyerang', 'serang', 'pukul'],
        'skill': ['skill', 'jurus', 'sihir'],
        'damage': ['terluka', 'kena'],
        'death': ['mati', 'tewas', 'hancur'],
        'stun': ['stun', 'pingsan'],
    }
    
    CHARS = {
        'black_knight': ['black knight', 'knight'],
        'vampire': ['vampire'],
        'skeleton': ['skeleton'],
        'ghost': ['ghost', 'hantu'],
        'pumpkin': ['pumpkin', 'labu'],
        'mira': ['mira'],
        'red_ninja': ['ninja'],
        'red_zoro': ['zoro'],
        'red_spider': ['spider'],
        'red_viking': ['viking'],
        'ent': ['ent', 'pohon'],
    }
    
    def action(self, text):
        text = text.lower()
        for a, kws in self.ACTIONS.items():
            for kw in kws:
                if kw in text:
                    return a
        return 'stand'
    
    def char(self, text):
        text = text.lower()
        for c, kws in self.CHARS.items():
            for kw in kws:
                if kw in text:
                    return c
        return None
    
    def bg(self, text):
        text = text.lower()
        if 'hutan' in text: return 'dark forest night'
        if 'kuil' in text: return 'ancient temple'
        if 'desa' in text: return 'village night'
        return 'dark scary night'

class VideoGenerator:
    def __init__(self):
        self.parser = CharacterParser()
        self.bg_dl = BackgroundDownloader()
        self.detector = StoryDetector()
    
    def add_watermark_top(self, image):
        """Watermark KECIL di ATAS - Keren & Terbaca"""
        draw = ImageDraw.Draw(image)
        
        # Font kecil
        try:
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
        except:
            font_small = ImageFont.load_default()
            font_bold = font_small
        
        # Background semi-transparent kecil di atas
        draw.rounded_rectangle([8, 8, WIDTH-8, 55], radius=8, fill=(0, 0, 0, 100))
        
        # Garis aksen
        draw.line([(15, 30), (WIDTH-15, 30)], fill=(255, 200, 50, 100), width=1)
        
        # Text watermark
        text1 = "YT: CeritaMistery"
        bbox1 = draw.textbbox((0, 0), text1, font=font_bold)
        x1 = (WIDTH - (bbox1[2]-bbox1[0])) // 2
        draw.text((x1+1, 12), text1, fill="black", font=font_bold)
        draw.text((x1, 11), text1, fill=(255, 255, 255, 200), font=font_bold)
        
        # Text YADSTORES
        text2 = "Top Up: yadstores.web.app"
        bbox2 = draw.textbbox((0, 0), text2, font=font_small)
        x2 = (WIDTH - (bbox2[2]-bbox2[0])) // 2
        draw.text((x2+1, 33), text2, fill="black", font=font_small)
        draw.text((x2, 32), text2, fill=(255, 200, 50, 200), font=font_small)
        
        return image
    
    def split_parts(self, cerita):
        words = cerita.split()
        wpp = int(PART_DURATION * 2.5)
        if len(words) <= wpp:
            return [cerita]
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', cerita) if s.strip()]
        parts = []
        current = []
        cw = 0
        for s in sentences:
            sw = len(s.split())
            if cw + sw > wpp:
                if current:
                    parts.append('. '.join(current) + '.')
                current = [s]
                cw = sw
            else:
                current.append(s)
                cw += sw
        if current:
            parts.append('. '.join(current) + '.')
        return parts
    
    def generate_part(self, cerita_part, part_num):
        print(f"\n🎬 Part {part_num}")
        
        tts = gTTS(text=cerita_part, lang="id", slow=False)
        audio_file = f"temp_part{part_num}.mp3"
        tts.save(audio_file)
        audio = AudioFileClip(audio_file)
        duration = audio.duration
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', cerita_part) if s.strip()]
        
        scenes = []
        for s in sentences:
            scenes.append({
                'text': s,
                'action': self.detector.action(s),
                'char': self.detector.char(s),
                'bg': self.detector.bg(s),
                'duration': max(len(s.split()) / 2.5, 2.0)
            })
        
        for scene in scenes:
            scene['bg_img'] = self.bg_dl.get_bg(scene['bg'])
        
        total_frames = int(duration * FPS)
        fps_scene = total_frames // len(scenes) if scenes else total_frames
        
        frames = []
        for frame_num in range(total_frames):
            scene_idx = min(frame_num // fps_scene, len(scenes) - 1)
            scene = scenes[scene_idx]
            
            bg = scene['bg_img'].copy()
            
            if scene['char']:
                char_frames = self.parser.get_frames(scene['char'], scene['action'])
                if char_frames:
                    char_idx = (frame_num // 4) % len(char_frames)
                    sprite_path = char_frames[char_idx]
                    try:
                        sprite = Image.open(sprite_path).convert("RGBA")
                        max_w = int(WIDTH * 0.5)
                        max_h = int(HEIGHT * 0.35)
                        ratio = min(max_w / sprite.width, max_h / sprite.height)
                        nw = int(sprite.width * ratio)
                        nh = int(sprite.height * ratio)
                        sprite = sprite.resize((nw, nh), Image.LANCZOS)
                        x = (WIDTH - nw) // 2
                        y = HEIGHT - nh - 50
                        bg.paste(sprite, (x, y), sprite)
                    except:
                        pass
            
            # WATERMARK ATAS
            bg = self.add_watermark_top(bg)
            
            frames.append(np.array(bg))
            
            if frame_num % 100 == 0:
                print(f"  Frame {frame_num}/{total_frames}")
        
        video = ImageSequenceClip(frames, fps=FPS)
        video = video.with_audio(audio)
        
        os.makedirs("output", exist_ok=True)
        output = f"output/part_{part_num}.mp4"
        video.write_videofile(output, fps=FPS, codec="libx264", audio_codec="aac", bitrate="800k", preset="ultrafast")
        video.close()
        audio.close()
        
        print(f"✅ Part {part_num} done!")
        return output
    
    def generate_all(self, cerita):
        parts = self.split_parts(cerita)
        print(f"\n📝 {len(parts)} parts")
        results = []
        for i, part in enumerate(parts):
            results.append(self.generate_part(part, i+1))
        return results

if __name__ == "__main__":
    gen = VideoGenerator()
    
    cerita = None
    if os.path.exists("cerita/cerita.txt"):
        with open("cerita/cerita.txt", "r") as f:
            cerita = f.read()
    if not cerita:
        cerita = "Black Knight berjalan di hutan gelap. Vampire muncul dan menyerang."
    
    results = gen.generate_all(cerita)
    print(f"\n✅ {len(results)} video!")
