"""Original CPU-only 2D puppet drama renderer. No paid or generative-video API.
Articulated actors, dialogue envelopes, backgrounds, props, weather and camera.
All state is isolated under a caller-selected project directory.
"""
import json,math,subprocess,wave,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H,FPS=1280,720,12
FONT=Path(__file__).resolve().parents[1]/'assets/fonts/NotoSansBengali.ttf'
def font(n):return ImageFont.truetype(str(FONT),n)
def probe(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def run(args):subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error',*map(str,args)],check=True,timeout=300)
def label(d,xy,t,size,fill,anchor=None):d.text(xy,t,font=font(size),fill=fill,anchor=anchor,stroke_width=0)
def background(kind):
 # Hand-built graphic-novel set with invariant geography: desk left, locked door right.
 im=Image.new('RGB',(W,H));p=np.zeros((H,W,3),dtype=np.uint8)
 for y in range(H):
  for c,v in enumerate((26,39,47)):p[y,:,c]=v+int(18*y/H)
 im=Image.fromarray(p);d=ImageDraw.Draw(im)
 if kind=='mina':
  d.rectangle((0,0,W,H),fill='#263548');d.rectangle((80,65,460,485),fill='#111e30',outline='#71919e',width=8)
  for x in (170,290,410):d.line((x,70,x,480),fill='#38536c',width=4)
  d.rectangle((0,510,W,H),fill='#44434c');d.rectangle((760,160,1160,450),fill='#5b625f',outline='#7c8980',width=6)
  for i in range(8):d.rectangle((790+i*42,250-(i%3)*30,820+i*42,440),fill=['#b68a67','#5b7278','#96704f'][i%3])
  d.rectangle((735,448,1190,465),fill='#252c33');d.ellipse((85,370,440,760),fill='#66535a')
 else:
  # Perspective wall, floorboards, rain window, framed family silhouette.
  d.polygon([(0,505),(1280,505),(1280,720),(0,720)],fill='#262d30')
  for x in range(-600,1900,160):d.line((640,505,x,720),fill='#535044',width=2)
  for y in (538,586,660):d.line((0,y,1280,y),fill='#1b252c',width=4)
  d.rectangle((85,90,405,410),fill='#101c29',outline='#65706b',width=10)
  for x in (190,298):d.line((x,95,x,405),fill='#45565d',width=7)
  d.line((90,245,400,245),fill='#45565d',width=7)
  d.rectangle((900,60,1205,550),fill='#101d26',outline='#697068',width=12)
  d.rectangle((930,85,1178,531),fill='#324147')
  for y in (105,305):d.rectangle((950,y,1156,y+165),fill='#2b383e',outline='#53605a',width=4)
  d.ellipse((1148,300,1167,319),fill='#c3aa70');d.rectangle((1099,298,1133,332),fill='#8b9188')
  d.arc((1103,280,1129,315),180,360,fill='#c1b38e',width=5)
  d.rectangle((490,80,660,270),fill='#a39170');d.rectangle((500,90,650,260),fill='#17262b')
  d.ellipse((545,118,606,182),fill='#6a7269');d.polygon([(523,246),(536,190),(610,187),(636,246)],fill='#4a605c')
  d.rectangle((45,480,700,506),fill='#7e684e');d.polygon([(45,506),(700,506),(710,544),(25,544)],fill='#413d36')
  for x in (65,630):d.rectangle((x,535,x+20,690),fill='#272f30')
  d.line((690,475,721,290),fill='#a18c60',width=8);d.polygon([(645,290),(776,290),(745,230),(678,230)],fill='#d1b778')
  for r in range(6):d.ellipse((610-r*9,270-r*6,810+r*9,540+r*4),outline=(66+r*2,65+r*2,49),width=2)
  d.ellipse((177,457,247,480),fill='#968e77');d.rectangle((183,427,239,466),fill='#b4ad95');d.arc((228,429,258,458),-90,90,fill='#b4ad95',width=6)
 return im
BGS={k:background(k) for k in ('room','mina')}

def actor(name,t,speaking,action,scale=1,flip=False):
 """Consistent character rig; articulated arms, gaze, brows, jaw and blink."""
 im=Image.new('RGBA',(340,610));d=ImageDraw.Draw(im)
 female=name!='rafi';older=name=='hazera'
 skin='#b68a6b' if not older else '#a4826c';shade='#7e5b49';ink='#16232a'
 shirt='#8c6c4b' if name=='rafi' else '#426d76' if name=='mina' else '#73667d'
 bob=math.sin(t*2.2)*2;cx=170+int(math.sin(t*.85)*3);hy=130+bob
 if action=='fear':hy-=3
 # Legs, shoes and torso with collar folds.
 d.polygon([(101,410),(162,410),(153,565),(115,565)],fill='#273642')
 d.polygon([(166,410),(224,410),(229,565),(187,565)],fill='#1c2c35')
 d.rounded_rectangle((102,555,157,581),10,fill=ink);d.rounded_rectangle((183,555,244,581),10,fill=ink)
 d.polygon([(107,252),(139,236),(199,236),(231,255),(224,425),(100,425)],fill=shirt,outline=ink,width=3)
 d.polygon([(126,244),(162,278),(177,254),(208,240),(186,298),(152,284)],fill='#ab936b' if not female else '#658d90')
 d.line((164,290,163,419),fill='#5c533e' if not female else '#35545e',width=3)
 for y in (302,340,378):d.ellipse((173,y,178,y+5),fill='#c8b58a')
 d.line((113,308,109,399),fill='#66503c',width=3);d.line((218,310,217,402),fill='#4c5553',width=3)
 # Neck and hair behind face.
 d.rounded_rectangle((147,210,187,256),10,fill=shade)
 if female:d.ellipse((104,62,229,264),fill='#20232b')
 d.ellipse((cx-60,hy-65,cx+53,hy+94),fill=skin,outline=ink,width=3)
 d.polygon([(cx-57,hy+10),(cx-47,hy+74),(cx-16,hy+95),(cx+22,hy+87),(cx+42,hy+51),(cx+30,hy+78),(cx-13,hy+84)],fill=shade)
 # Hair is fixed identity, never generated afresh.
 d.pieslice((cx-62,hy-77,cx+55,hy+23),180,360,fill='#202329')
 d.polygon([(cx-61,hy-20),(cx-42,hy-64),(cx+47,hy-44),(cx+55,hy-2),(cx+29,hy-35),(cx-32,hy-28),(cx-51,hy+15)],fill='#202329')
 if older:
  for dx in (-35,-10,15,32):d.line((cx+dx,hy-59,cx+dx+10,hy-36),fill='#9a9f97',width=3)
 if not female:
  for dx in range(-30,36,8):d.line((cx+dx,hy+66,cx+dx+2,hy+72),fill='#514039',width=2)
 # Face eyes and expressive eyebrows; short blinks every ~4s.
 blink=(t%4.7)<.12;eyeY=hy+6
 for ex in (cx-27,cx+22):
  if blink:d.line((ex-12,eyeY,ex+12,eyeY+1),fill=ink,width=3)
  else:
   d.ellipse((ex-13,eyeY-5,ex+13,eyeY+7),fill='#e0d7bc');d.ellipse((ex-3,eyeY-4,ex+5,eyeY+7),fill=ink)
  by=eyeY-16-(4 if action in ('fear','concern','warn') else 0)
  d.line((ex-14,by+3,ex,by,ex+13,by+2),fill=ink,width=4)
 d.line((cx+1,hy+15,cx-3,hy+38,cx+10,hy+40),fill=shade,width=3)
 if speaking>.1:
  opening=3+int(speaking*13);d.ellipse((cx-17,hy+57-opening/3,cx+16,hy+58+opening),fill='#412f30')
  d.rectangle((cx-12,hy+56,cx+11,hy+59),fill='#e1cbb1')
 elif action=='smile':d.arc((cx-20,hy+43,cx+20,hy+65),0,180,fill='#5f4039',width=3)
 else:d.line((cx-14,hy+59,cx+13,hy+59),fill='#60423a',width=3)
 if older:
  for ey in (hy+19,hy+24):d.line((cx-47,ey,cx-31,ey+2),fill=shade,width=1)
  # Sari scarf framing the head, preserving her distinctive silhouette.
  d.arc((cx-76,hy-85,cx+72,hy+130),170,370,fill='#9c8b9f',width=15)
  d.polygon([(217,223),(253,333),(219,426),(197,276)],fill='#97879c')
 # Arms rotate and gesture with visible elbow and hand displacement.
 wave=math.sin(t*3.2)*5;left=(96,350+wave);right=(242,351-wave)
 if action in ('phone','concern','listen'):right=(228,170+wave*.2)
 elif action in ('reach','play','inspect','point'):right=(300,295+wave)
 elif action in ('fear','back','warn'):right=(273,285+wave)
 elif action in ('talk','smile','shrug','touch','sad','soft'):right=(268,323+wave*1.6)
 for shoulder,elbow,hand in [((111,267),(85,319),left),((224,269),(251,315),right)]:
  d.line((shoulder,elbow),fill=shirt,width=32);d.line((elbow,hand),fill=shirt,width=25)
  hx,hy2=hand;d.ellipse((hx-13,hy2-12,hx+13,hy2+16),fill=skin,outline=shade,width=2)
 if action in ('phone','concern','listen'):
  hx,hy2=right;d.rounded_rectangle((hx-8,hy2-33,hx+14,hy2+18),4,fill='#111e29',outline='#899b9e',width=2)
 if action=='bag':d.rounded_rectangle((243,350,315,440),10,fill='#4b3c33');d.arc((251,323,303,378),180,360,fill='#9b805c',width=5)
 if flip:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 if scale!=1:im=im.resize((int(340*scale),int(610*scale)),Image.Resampling.BICUBIC)
 return im

def tape(d,t,large=False):
 x,y,w,h=(200,265,860,310) if large else (332,425,280,85)
 d.rounded_rectangle((x,y,x+w,y+h),14,fill='#243239',outline='#98a49a',width=4)
 d.rounded_rectangle((x+w*.1,y+h*.16,x+w*.9,y+h*.65),8,fill='#111e26',outline='#5d6c6e',width=3)
 for xx in (x+w*.31,x+w*.69):
  cy=y+h*.4;r=h*.18;d.ellipse((xx-r,cy-r,xx+r,cy+r),fill='#8c9b97',outline='#c0c4ad',width=3)
  for j in range(3):
   a=t*2+j*math.tau/3;d.line((xx,cy,xx+math.cos(a)*r*.85,cy+math.sin(a)*r*.85),fill='#263039',width=4)
 for j in range(5):d.rectangle((x+w*(.14+j*.145),y+h*.78,x+w*(.24+j*.145),y+h*.94),fill='#697670')
 d.ellipse((x+w*.92,y+h*.1,x+w*.94,y+h*.16),fill='#e47f57')

def wrap(txt,n=52):
 lines=[];line=''
 for word in txt.split():
  if len(line+' '+word)>n:lines.append(line);line=word
  else:line=(line+' '+word).strip()
 if line:lines.append(line)
 return lines

def frame(s,t,energy):
 view=s['view'];speaker=s['speaker'];action=s['action']
 im=BGS['mina' if view=='mina' else 'room'].copy();d=ImageDraw.Draw(im)
 # Window rain moves independently; only exterior rain stops near the climax.
 if view!='mina' and s['start']<280:
  for i in range(52):
   x=95+(i*59)%305;y=99+(i*83+t*150)%302;d.line((x,y,x-5,min(405,y+22)),fill='#647a86',width=1)
 def place(name,x,y,scale=1,flip=False):
  e=energy if speaker==name else 0
  rig=actor(name,t,e,action if speaker==name else 'listen',scale,flip)
  if action in ('walk','leave') and name==speaker:x+=int((t/7.5-.5)*130)
  im.paste(rig,(int(x),int(y)),rig)
 if view=='arrival':place('rafi',530,75,.95);place('hazera',800,90,.9,True)
 elif view=='two':place('rafi',300,90,.96);place('hazera',740,100,.94,True)
 elif view=='hazera_close':place('hazera',440,45,1.45)
 elif view=='rafi_close':place('rafi',435,35,1.45)
 elif view=='mina':place('mina',440,35,1.45)
 elif view in ('desk','hall'):place('rafi',400 if view=='desk' else 650,95,1.0)
 elif view=='door':place('rafi',460,180,.83,True)
 if view=='tape':
  d.rectangle((0,0,W,H),fill='#17252d');d.polygon([(0,360),(1280,240),(1280,720),(0,720)],fill='#63523d');tape(d,t,True)
 elif view in ('desk','two','arrival'):tape(d,t)
 d=ImageDraw.Draw(im)
 if view=='door' and s['start']>275:
  # Water spreads out from underneath the same door.
  wide=100+int(t*24);d.ellipse((1060-wide,535,1180+wide,555+t*9),fill='#51727b')
 if view=='title':
  d.rectangle((0,0,W,H),fill='#15242d');label(d,(640,255),'ঘর ১:১৭',86,'#e0c49a','mm');label(d,(640,353),'পর্ব ১ · না-বলা কথা',34,'#a5bbb9','mm');label(d,(640,440),'এক ঘণ্টা আগে',24,'#7f999e','mm')
  d.line((350,400,930,400),fill='#907353',width=2)
  points=[(x,520+math.sin(x*.05-t*4)*math.sin((x-300)/680*math.pi)*18) for x in range(300,981,4)];d.line(points,fill='#9aaea8',width=3)
 # Subtle cinematic push-in, not the source of character motion.
 z=1+.018*t/7.5;cw=int(W/z);ch=int(H/z);im=im.crop(((W-cw)//2,(H-ch)//2,(W+cw)//2,(H+ch)//2)).resize((W,H),Image.Resampling.BILINEAR)
 d=ImageDraw.Draw(im);d.rectangle((0,0,W,37),fill='#101b24');d.rectangle((0,638,W,H),fill='#101b24')
 label(d,(35,18),'নিশিকথা   /   ঘর ১:১৭',17,'#9eaa9f','lm');label(d,(1245,18),'2D অ্যানিমেটেড ডেমো',15,'#81959b','rm')
 if s['text']:
  lines=wrap(s['text']);n=len(lines);sz=25 if n<3 else 22
  for i,line in enumerate(lines):label(d,(640,650+i*29),line,sz,'#ece7d3','mt')
 if s['id']=='040' and t>5.5:label(d,(640,580),'চলবে · পর্ব ২: ঘরের ভেতরের ফোন',28,'#dfbd89','mm')
 return im

def render(project,root):
 project=Path(project);root=Path(root);root.mkdir(parents=True,exist_ok=True)
 plan=json.loads((project/'plan.json').read_text());clips=[];subs=[]
 for s in plan['shots']:
  dest=root/(s['id']+'.mp4');clips.append(dest)
  if dest.exists() and abs(float(probe(dest)['format']['duration'])-s['seconds'])<.1:continue
  voice=root/(s['id']+'.mp3');wav=root/(s['id']+'.wav')
  speed=1.
  if s['text']:
   if not voice.exists():raise ValueError('Dialogue not yet produced: '+s['id'])
   dur=float(probe(voice)['format']['duration']);speed=max(1,dur/(s['seconds']-.6))
   if speed>1.35:raise ValueError('Dialogue too long: '+s['id']+' '+str(dur))
   filt=f'atempo={speed},adelay=200,apad,atrim=duration={s["seconds"]}'
   if s['speaker']=='echo':filt+=' ,highpass=f=300,lowpass=f=2600,aecho=0.8:0.45:90:0.2'
   run(['-i',voice,'-af',filt,'-ar',24000,'-ac',1,wav])
   with wave.open(str(wav),'rb') as w:a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
  else:a=np.zeros(int(s['seconds']*24000));
  raw=root/(s['id']+'.silent.mp4')
  proc=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(raw)],stdin=subprocess.PIPE)
  for f in range(round(s['seconds']*FPS)):
   t=f/FPS;chunk=a[int(t*24000):int((t+.055)*24000)];e=min(1,float(np.sqrt(np.mean(chunk**2)))*12) if len(chunk) else 0
   proc.stdin.write(frame(s,t,e).tobytes())
  proc.stdin.close()
  if proc.wait()!=0:raise ValueError('Frame encode failed')
  if not s['text']:
   with wave.open(str(wav),'wb') as w:w.setparams((1,2,24000,0,'NONE',''));w.writeframes((a*32767).astype('<i2').tobytes())
  run(['-i',raw,'-i',wav,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-t',s['seconds'],dest]);raw.unlink()
  print('ANIMATED SHOT',s['id'],'/40',flush=True)
 # Original synthesized score, rain, footsteps, door, tape, knocks and phone.
 from .free_episode import soundtrack
 soundtrack(root/'score.wav',300,[s['start'] for s in plan['shots']], [dict(foley={'tape':'metal','room':'none','rain':'none','door':'knocks','steps':'knocks'}.get(s['sfx'],s['sfx'])) for s in plan['shots']])
 from .media import timestamp
 for s in plan['shots']:
  if s['text']:subs.append(f'{len(subs)+1}\n{timestamp(s["start"]+.2)} --> {timestamp(s["start"]+s["seconds"])}\n{s["text"]}\n')
 (root/'subtitles.bn.srt').write_text('\n'.join(subs))
 (root/'concat.txt').write_text(''.join("file '"+p.name+"'\n" for p in clips))
 final=root/'Ghor_117_EP01_Animated_Drama.mp4'
 run(['-f','concat','-safe','0','-i',root/'concat.txt','-i',root/'score.wav','-i',root/'subtitles.bn.srt','-filter_complex','[0:a]asplit=2[v][side];[1:a][side]sidechaincompress=threshold=0.02:ratio=5:attack=10:release=350[b];[v][b]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.94[a]','-map','0:v','-map','[a]','-map','2:0','-t','300','-c:v','copy','-c:a','aac','-b:a','160k','-ac','2','-c:s','mov_text','-metadata:s:s:0','language=ben','-movflags','+faststart',final])
 info=probe(final);report=dict(file=final.name,seconds=float(info['format']['duration']),width=1280,height=720,fps=12,shots=40,cost_usd=0,kind=plan['output_kind'],neural_video=False)
 (root/'render.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
 return final
if __name__=='__main__':
 import sys
 render(sys.argv[1],sys.argv[2])
