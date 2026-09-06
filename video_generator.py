"""
🎮 LARVA ANIMATION GENERATOR - REAL SPRITE
Menggunakan animasi asli dari game
"""

import os
import re
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

try:
    from moviepy.editor import ImageSequenceClip, AudioFileClip
except:
    from moviepy import ImageSequenceClip, AudioFileClip

WIDTH = 360
HEIGHT = 640
FPS = 30
PART_DURATION = 120
ASSETS = "larva_assets"

class LarvaParser:
    def __init__(self):
        self.chars = {}
        self.parse()
    
    def parse(self):
        for root, dirs, files in os.walk(ASSETS):
            for f in files:
                if f.endswith('.png'):
                    parts = f.replace('.png','').split('_')
                    if len(parts) >= 3:
                        if len(parts) >= 4 and parts[1] in ['knight','warrior','ninja','zoro','spider','viking','terminator','iron']:
                            char = '_'.join(parts[:2])
                            anim = parts[2]
                        else:
                            char = parts[0]
                            anim = parts[1]
                        
                        if char not in self.chars:
                            self.chars[char] = {}
                        if anim not in self.chars[char]:
                            self.chars[char][anim] = []
                        self.chars[char][anim].append(os.path.join(root, f))
        
        for c in self.chars:
            for a in self.chars[c]:
                self.chars[c][a].sort()
        
        print(f"✅ {len(self.chars)} karakter")
    
    def get_frames(self, char, anim):
        if char in self.chars and anim in self.chars[char]:
            return self.chars[char][anim]
        for c in self.chars:
            for a in self.chars[c]:
                return self.chars[c][a]
        return []

class Detector:
    ACTIONS = {
        'walk': ['berjalan','jalan'],
        'run': ['berlari','lari'],
        'stand': ['berdiri','diam'],
        'attack': ['menyerang','serang'],
        'skill01': ['skill01','skill 1'],
        'skill02': ['skill02','skill 2'],
        'skill03': ['skill03','skill 3'],
        'skill04': ['skill04','skill 4'],
        'damage': ['terluka','kena'],
        'death': ['mati','tewas','hancur'],
        'stun': ['stun','pingsan'],
    }
    
    CHARS = {
        'black_knight': ['black knight','knight'],
        'vampire': ['vampire'],
        'skeleton': ['skeleton'],
        'ghost': ['ghost','hantu'],
        'pumpkin': ['pumpkin','labu'],
        'mira': ['mira'],
        'red_ninja': ['ninja'],
        'red_zoro': ['zoro'],
        'red_spider': ['spider'],
        'red_viking': ['viking'],
        'ent': ['ent','pohon'],
    }
    
    def action(self, text):
        tl = text.lower()
        for a, kws in self.ACTIONS.items():
            for kw in kws:
                if kw in tl:
                    return a
        return 'stand'
    
    def char(self, text):
        tl = text.lower()
        for c, kws in self.CHARS.items():
            for kw in kws:
                if kw in tl:
                    return c
        return None

class Generator:
    def __init__(self):
        self.parser = LarvaParser()
        self.detector = Detector()
    
    def watermark(self, img):
        d = ImageDraw.Draw(img)
        try:
            fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
            fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            fb = fs = ImageFont.load_default()
        
        d.rounded_rectangle([8,8,WIDTH-8,55], radius=8, fill=(0,0,0,100))
        t1 = "YT: CeritaMistery"
        b1 = d.textbbox((0,0), t1, font=fb)
        d.text(((WIDTH-(b1[2]-b1[0]))//2+1, 12), t1, fill="black", font=fb)
        d.text(((WIDTH-(b1[2]-b1[0]))//2, 11), t1, fill=(255,255,255,200), font=fb)
        
        t2 = "Top Up: yadstores.web.app"
        b2 = d.textbbox((0,0), t2, font=fs)
        d.text(((WIDTH-(b2[2]-b2[0]))//2+1, 33), t2, fill="black", font=fs)
        d.text(((WIDTH-(b2[2]-b2[0]))//2, 32), t2, fill=(255,200,50,200), font=fs)
        return img
    
    def bg(self, seed=0):
        img = Image.new("RGB", (WIDTH, HEIGHT), (30,30,50))
        d = ImageDraw.Draw(img)
        for y in range(HEIGHT):
            f = y/HEIGHT
            d.line([(0,y),(WIDTH,y)], fill=(int(30*(1-f*0.5)), int(30*(1-f*0.5)), int(50*(1-f*0.5))))
        d.rectangle([(0,HEIGHT-80),(WIDTH,HEIGHT)], fill=(40,35,25))
        return img
    
    def generate(self, cerita):
        sentences = [s.strip() for s in re.split(r'[.!?]+', cerita) if s.strip()]
        
        tts = gTTS(text=cerita[:500], lang='id', slow=False)
        tts.save("audio.mp3")
        audio = AudioFileClip("audio.mp3")
        duration = min(audio.duration, PART_DURATION)
        
        total_frames = int(duration * FPS)
        fps_scene = total_frames // len(sentences) if sentences else total_frames
        
        frames = []
        for fn in range(total_frames):
            si = min(fn // fps_scene, len(sentences)-1)
            s = sentences[si]
            
            img = self.bg(si)
            
            char = self.detector.char(s)
            action = self.detector.action(s)
            
            if char:
                cf = self.parser.get_frames(char, action)
                if cf:
                    # ANIMASI LAMBAT: ganti setiap 4 frame
                    idx = (fn // 4) % len(cf)
                    sprite = Image.open(cf[idx]).convert("RGBA")
                    
                    mw = int(WIDTH * 0.6)
                    mh = int(HEIGHT * 0.4)
                    ratio = min(mw/sprite.width, mh/sprite.height)
                    nw = int(sprite.width * ratio)
                    nh = int(sprite.height * ratio)
                    sprite = sprite.resize((nw, nh), Image.LANCZOS)
                    
                    x = (WIDTH - nw) // 2
                    y = HEIGHT - nh - 60
                    
                    img.paste(sprite, (x, y), sprite)
            
            img = self.watermark(img)
            frames.append(np.array(img))
        
        video = ImageSequenceClip(frames, fps=FPS)
        video = video.set_audio(audio)
        
        os.makedirs("output", exist_ok=True)
        video.write_videofile("output/larva_animated.mp4", fps=FPS, codec="libx264", audio_codec="aac", bitrate="800k", verbose=False)
        video.close()
        
        return "output/larva_animated.mp4"

gen = Generator()
result = gen.generate("
RITUAL KEGELAPAN - Cerita Horor

---

PART 1 - Rumah Tua di Ujung Jalan

Malam itu hujan deras mengguyur kota. Sarah terpaksa berteduh di sebuah rumah tua di ujung jalan yang sudah lama ditinggalkan. Pintu kayu yang lapuk terbuka dengan sendirinya, mengeluarkan bau busuk yang menusuk hidung.

Di dalam, lilin-lilin menyala tanpa api. Bayangan-bayangan bergerak di dinding meski tidak ada orang. Dari lantai dua, terdengar suara langkah kaki mendekat perlahan.

"Kau seharusnya tidak datang ke sini," bisik sebuah suara dari balik pintu.

Sarah berbalik, dan di hadapannya berdiri sesosok wanita berpakaian putih dengan wajah yang membusuk. Matanya hitam pekat menatap kosong. Wanita itu tersenyum, memperlihatkan gigi-gigi yang menghitam.

"Bergabunglah dengan kami," katanya sambil mengulurkan tangan yang tinggal tulang.

Sarah menjerit dan berlari, tetapi setiap pintu yang ia buka membawanya kembali ke ruangan yang sama. Dinding-dinding mulai mengeluarkan darah hitam pekat.

Tiba-tiba, lantai di bawahnya runtuh. Sarah jatuh ke ruang bawah tanah yang gelap. Di sana, puluhan mayat bergelantungan dengan mata terbuka. Mereka semua menatap ke arah Sarah.

"Sekarang giliranmu," suara itu berbisik tepat di telinganya.

---

PART 2 - Ruang Bawah Tanah

Sarah terbangun di ruangan gelap yang lembab. Tangan dan kakinya terikat di meja batu. Di sekelilingnya, lilin-lilin merah menyala membentuk lingkaran. Simbol-simbol aneh digambar dengan darah di lantai.

Seorang pria tua berpakaian jubah hitam berdiri di dekatnya sambil memegang belati perak. Wajahnya penuh bekas luka, dan matanya bersinar merah seperti bara api.

"Jangan melawan, anakku. Ini akan cepat," bisiknya sambil mengasah belati.

Sarah berjuang melepaskan ikatan. Tali yang mengikatnya terbuat dari rambut manusia, dan semakin ia meronta, semakin kencang tali itu menjerat.

Di sudut ruangan, sesosok makhluk tinggi dengan kulit abu-abu mulai merangkak mendekat. Jari-jarinya yang panjang menggores lantai batu, mengeluarkan suara yang membuat bulu kuduk berdiri.

"Pembunuh itu datang," kata pria tua itu sambil tersenyum. "Ia lapar akan jiwa-jiwa yang suci."

Makhluk itu melompat ke arah Sarah dengan rahang terbuka lebar. Gigi-giginya yang tajam berkilat dalam cahaya lilin.

Sarah menendang meja batu dengan sekuat tenaga. Meja itu terbalik, menimpa pria tua itu. Belatinya terlepas dan meluncur ke arah Sarah.

Dengan cepat, Sarah meraih belati itu dan memotong talinya. Makhluk abu-abu itu menyerang lagi, tetapi Sarah menusuk matanya dengan belati.

Jeritan mengerikan mengguncang ruangan. Darah hitam muncrat ke mana-mana.

---

PART 3 - Pelarian dari Kegelapan

Sarah berlari menyusuri koridor gelap. Di belakangnya, langkah-langkah berat mengejar. Makhluk itu tidak mati, hanya terluka. Ia kini semakin marah dan haus darah.

Dinding-dinding koridor mulai menutup, mempersempit jalan. Tangan-tangan mayat muncul dari balik batu, mencengkeram kaki Sarah.

"Tidak ada jalan keluar," suara itu bergema. "Kau akan mati di sini bersama kami."

Sarah terus berlari, meskipun paru-parunya terbakar. Di ujung koridor, ia melihat sebuah pintu kayu dengan ukiran pentagram.

Ia mendobrak pintu itu dan masuk ke sebuah ruangan besar. Di tengah ruangan, terdapat altar dengan mayat seorang gadis yang masih segar. Darahnya menetes ke lantai, membentuk kolam merah.

"Persembahan berikutnya adalah kau," wanita berpakaian putih itu muncul dari bayangan.

Sarah mengangkat belatinya. "Aku tidak akan mati di sini!" teriaknya.

Wanita itu tertawa. "Semua orang bilang begitu, sayangku. Tapi lihat mereka sekarang."

Ia menunjuk ke arah dinding. Ratusan wajah terpahat di batu, semuanya berteriak dalam kesakitan abadi.

Sarah menyerang dengan belatinya, tetapi wanita itu menghilang dalam asap hitam.

---

PART 4 - Pertarungan di Altar

Dari kegelapan, makhluk abu-abu itu muncul kembali. Matanya yang terluka mengeluarkan cairan hitam, dan tubuhnya kini berubah semakin mengerikan. Tulang-tulangnya mencuat dari kulit, membentuk duri-duri tajam.

Sarah bersiap menghadapi makhluk itu. Belati perak di tangannya bersinar samar dalam kegelapan.

Makhluk itu menyerang dengan cakar raksasanya. Sarah melompat ke samping, menghindari serangan yang menggores lantai batu seperti pisau memotong mentega.

"Belati itu tidak akan bisa membunuhku!" raung makhluk itu.

Sarah menyerang balik, menusuk kaki makhluk itu. Makhluk itu menjerit kesakitan dan menghantamkan ekornya ke dinding, membuat batu-batu berjatuhan.

Di saat yang sama, pria tua berjubah hitam itu muncul dari balik altar. Wajahnya berdarah, dan belati lain di tangannya.

"Kau membunuhku sekali, tapi aku bangkit lagi!" katanya sambil menyerang.

Sarah menghindari serangannya, lalu menendang pria itu ke arah makhluk abu-abu. Kedua makhluk jahat itu bertabrakan.

Memanfaatkan kekacauan, Sarah menusuk punggung pria tua itu. Darah menyembur keluar, dan pria itu jatuh ke lantai dengan jeritan mengerikan.

Makhluk abu-abu itu meraung marah dan menyerang Sarah dengan kekuatan penuh.

---

PART 5 - Pembunuhan Pria Tua

Pria tua itu masih hidup, merangkak di lantai dengan darah mengalir dari luka di punggungnya. Sarah tahu ia harus menghabisinya sebelum pria itu bangkit lagi.

"Kau pikir kau bisa membunuhku?" pria itu tertawa getir. "Aku sudah mati seratus tahun yang lalu!"

Sarah berdiri di atasnya. "Kalau begitu, kau tidak akan keberatan mati sekali lagi."

Ia mengangkat belati tinggi-tinggi, lalu menikamkannya tepat ke jantung pria tua itu. Pria itu menjerit, tubuhnya menggeliat seperti cacing yang dipotong.

Darah hitam menyembur dari lukanya, mengenai wajah Sarah. Namun ia tidak berhenti. Ia mencabut belatinya dan menikamkan lagi, lagi, dan lagi.

Setiap tusukan membuat pria itu semakin melemah. Kulitnya mulai mengelupas, memperlihatkan daging yang membusuk di bawahnya.

"Ini... belum... berakhir..." bisik pria itu dengan napas terakhirnya.

Tubuhnya hancur menjadi debu hitam, tertiup angin entah dari mana.

---

PART 6 - Makhluk Kegelapan

Makhluk abu-abu itu meraung melihat kematian tuannya. Kemarahannya berubah menjadi kekuatan yang mengerikan. Tubuhnya membesar, otot-ototnya menonjol, dan matanya menyala merah.

"KAU MEMBUNUH TUANKU!" raungnya, suaranya menggetarkan seluruh ruangan.

Sarah menggenggam belatinya erat-erat. Tangannya gemetar, tapi matanya penuh tekad.

"Aku juga akan membunuhmu!" teriaknya menantang.

Makhluk itu menyerang dengan kecepatan kilat. Cakarnya menggores lengan Sarah, membuat darah mengalir. Sarah menjerit kesakitan, tapi tidak mundur.

Ia melompat ke atas altar, lalu melompat lagi ke punggung makhluk itu. Belatinya ia tancapkan ke leher makhluk itu.

Makhluk itu mengamuk, mencoba melepaskan Sarah dari punggungnya. Ia menghantamkan tubuhnya ke dinding, ke lantai, ke mana-mana.

Sarah bertahan, terus menusuk leher makhluk itu berulang kali. Darah hitam muncrat ke wajahnya, tapi ia tidak peduli.

"MATI KAU, MONSTER!" teriaknya.

---

PART 7 - Luka di Kegelapan

Sarah terpental dan jatuh ke lantai. Lengannya berdarah, tulang rusuknya mungkin retak. Makhluk itu masih hidup, meskipun lehernya penuh luka.

"Kau... tidak bisa... membunuhku..." makhluk itu terengah-engah.

Sarah mencoba bangkit, tapi kakinya gemetar. Rasa sakit menjalar ke seluruh tubuhnya.

"Aku sudah sejauh ini," bisiknya pada dirinya sendiri. "Aku tidak bisa menyerah sekarang."

Ia melihat belatinya tergeletak beberapa meter darinya. Ia merangkak, mengabaikan rasa sakit yang menusuk.

Makhluk itu juga bergerak mendekat, menyeret tubuhnya yang terluka. Keduanya berlomba menuju belati.

Sarah meraih belatinya lebih dulu. Dengan sisa tenaga, ia menusuk mata makhluk itu yang satunya lagi.

Makhluk itu menjerit dan menghantamkan cakarnya ke dada Sarah. Sarah terpental jauh, menghantam dinding batu.

Gelap mulai menyelimuti pandangannya. Darah mengalir dari luka di dadanya.

"Apakah ini akhir?" pikirnya.

Tapi kemudian, ia mendengar suara. Suara yang memberinya harapan.

---

PART 8 - Kebangkitan Terakhir

Di tengah kegelapan, Sarah melihat cahaya. Cahaya itu berasal dari belatinya yang kini menyala terang. Belati perak itu menyerap darah makhluk kegelapan dan berubah menjadi senjata suci.

"Belati itu... adalah satu-satunya yang bisa membunuhku..." suara wanita berpakaian putih itu muncul kembali.

Sarah memandang belatinya yang bersinar. Ia merasakan kekuatan baru mengalir di tubuhnya. Luka-lukanya mulai menutup, rasa sakitnya hilang.

"Aku mengerti sekarang," kata Sarah. "Ini bukan belati biasa."

Wanita putih itu tersenyum tipis. "Itu adalah belati yang sama yang membunuhku seratus tahun lalu. Dan sekarang, kau harus menggunakannya untuk mengakhiri semuanya."

Sarah bangkit. Tubuhnya kini penuh kekuatan. Belati di tangannya menyala seperti obor di tengah kegelapan.

Makhluk abu-abu itu meraung ketakutan melihat cahaya itu. Ia mencoba mundur, tapi Sarah sudah siap.

"Sekarang, monster," kata Sarah, "giliranmu untuk merasakan sakit."

---

PART 9 - Pertarungan Final

Sarah menyerang dengan kecepatan yang tidak pernah ia bayangkan. Belati suci itu memotong daging makhluk itu seperti mentega panas.

Makhluk abu-abu itu meraung, mencoba menyerang balik dengan cakarnya. Tapi setiap kali cakarnya mendekat, belati Sarah memotongnya.

"TIDAK MUNGKIN!" raung makhluk itu. "AKU TIDAK BISA DIBUNUH!"

"Semua makhluk bisa dibunuh," jawab Sarah sambil menusuk perut makhluk itu.

Makhluk itu terhuyung. Darah hitam mengalir deras dari lukanya. Ia jatuh berlutut di hadapan Sarah.

"Aku... akan kembali..." bisiknya.

"Tidak, kau tidak akan," kata Sarah.

Ia mengangkat belatinya tinggi-tinggi, lalu menikamkannya tepat ke jantung makhluk itu. Makhluk itu menjerit satu kali, lalu tubuhnya hancur menjadi abu.

Keheningan menyelimuti ruangan. Pertarungan telah berakhir.

---

PART 10 - Kemenangan dan Kedamaian

Sarah berdiri di tengah ruangan, terengah-engah. Di sekelilingnya, sisa-sisa abu makhluk kegelapan beterbangan.

Wanita berpakaian putih itu muncul sekali lagi. Wajahnya yang membusuk kini berubah menjadi wajah seorang gadis cantik.

"Terima kasih," katanya lembut. "Kau telah membebaskanku dari kutukan."

"Siapa kau sebenarnya?" tanya Sarah.

"Aku adalah korban pertama ritual ini. Seratus tahun yang lalu, mereka mengorbankanku untuk membangkitkan kegelapan. Jiwaku terperangkap, dipaksa menjadi pelayan kegelapan."

"Sekarang kau bebas," kata Sarah.

"Ya, berkat kau." Wanita itu tersenyum. "Pergilah, sebelum tempat ini runtuh. Kau telah menyelesaikan apa yang seharusnya kuselesaikan dulu."

Sarah berjalan keluar dari rumah tua itu. Saat matahari terbit, rumah itu runtuh di belakangnya, terkubur selamanya.

"Aku selamat," bisik Sarah. "Aku benar-benar selamat."

Ia memandang belati di tangannya yang kini tidak lagi bersinar. Belati itu sekarang hanyalah belati biasa, tetapi akan selalu mengingatkannya pada malam itu.

Sarah berjalan menjauh dari reruntuhan, meninggalkan kegelapan di belakangnya.

---

TAMAT")
print(f"✅ {result}")
